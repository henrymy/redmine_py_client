#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import base64
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import os
import smtplib
import yaml

from redminelib import Redmine, exceptions

import utils

class RedmineAPIClient:
    redmine = None

    def __init__(self, url, api_key):
        self.redmine = Redmine(url, key=api_key)

    # get all projects
    def get_all_prj(self):
        projects = self.redmine.project.all()
        return projects

    # get project by project id
    def get_prj_by_id(self, project_id):
        project_obj = None
        projects = self.get_all_prj()
        for prj in projects:
            if prj['identifier'] == project_id:
                project_obj = prj
                break
        return project_obj

    # get all subject projects in list
    # PARAM: parent project obj
    def get_sub_prj_list(self, parent_prj):
        sub_prj_list = []
        parent_prj_id = parent_prj.id
        projects = self.get_all_prj()
        for prj in projects:
            if not getattr(prj,'parent', False):
                continue
            if prj.parent.id == parent_prj_id:
                sub_prj_list.append(prj)
        return sub_prj_list
         
    # get all available statuses
    def get_all_status(self):
        statuses = self.redmine.issue_status.all()
        return statuses

    # get status obj by name
    def get_status_by_name(self, status_name):
        status = None
        statuses = self.get_all_status()
        for status in statuses:
            if status.name == status_name:
                break
        return status

    # get issue detail by issue id
    def get_issue_by_id(self, issue_id):
        issue_obj = self.redmine.issue.get(issue_id, include=['journals'])
        return issue_obj

    # get issues in project filtered by status
    def get_issues_by_prj_and_status(self, project, status):
        self.get_issues_by_prj_and_status_id(project, status.id)
        return issues

    # get issues in project filtered by status_id
    def get_issues_by_prj_and_status_id(self, project, status_id):
        issues = self.redmine.issue.filter(
            project_id=project.id, status_id=status_id)
        return issues

    # get all user obj
    def get_all_user(self):
        all_users = self.redmine.user.all()
        return user_obj
        
    # get user obj by user id
    def get_user_by_id(self, user_id):
        user_obj = self.redmine.user.get(user_id)
        return user_obj
        
    def get_issue_custom_fields(self, issue):
        custom_fields = getattr(issue,'custom_fields', None)
        if custom_fields:
            return custom_fields
        return []

    # get issue step info obj
    # input para: issue object
    # return value: custom field type obj
    def get_issue_step_info(self, issue):
        step_info_name = 'CKKB_STEP'
        custom_fields = self.get_issue_custom_fields(issue)
        for custom_field in custom_fields:
            if custom_field.name == step_info_name:
                return custom_field
        return None

    # get tickets working by certain user 
    def if_working_by_user(self, issue, user):
        # 1st: check assigned_to property
        if self.issue_assigned_to_user(issue, user):
            return True
        # 2nd: if currently not assigned, check journals too
        if self.issue_ever_assigned_to_user(issue, user):
            return True
        return False

    # get tickets working by certain user list 
    def if_working_by_user_list(self, issue, user_ids):
        # 1st: check assigned_to property
        if self.issue_assigned_to_user_list(issue, user_ids):
            return True
        # 2nd: if currently not assigned, check journals too
        if self.issue_ever_assigned_to_user_list(issue, user_ids):
            return True
        return False

    # check an issue is assigned to certain user
    def issue_assigned_to_user(self, issue, user):
        assigned_to = getattr(issue, 'assigned_to', None)
        if not assigned_to:
            return False 
        if assigned_to.id == user.id:
            return True
        return False 
        
    # check an issue is assigned to certain user list
    # input para1: issue obj
    # input para2: list of user ids
    # return true after hit first user_id
    def issue_assigned_to_user_list(self, issue, user_ids):
        assigned_to = getattr(issue, 'assigned_to', None)
        if not assigned_to:
            return False 
        if assigned_to.id in user_ids:
            return True
        return False 

    # check an issue has ever been assigned_to certain user
    # contidion: new value of assigned_to_id property in journal.details == user.id
    def issue_ever_assigned_to_user(self, issue, user):
        for journal in issue.journals:
            for record in journal.details:
                try:
                    if record['name'] == 'assigned_to_id' and int(record['new_value']) == user.id:
                        return True
                except KeyError:
                    pass
        return False 

    # check an issue has ever been assigned_to certain user list
    # contidion: new value of assigned_to_id property in journal.details in user_ids
    def issue_ever_assigned_to_user_list(self, issue, user_ids):
        for journal in issue.journals:
            for record in journal.details:
                try:
                    if record['name'] == 'assigned_to_id' and int(record['new_value']) in user_ids:
                        return True
                except KeyError:
                    pass
        return False 

    # get user obj by user name
    def get_user_by_name(self, username):
        pass
        
    # get all issues assigned to certain user
    def get_issues_assigned_to(self, user):
    # build a dict with user_id as keys to calculate number of working tickets
        pass

    def set_issue_property(self, issue, **kwargs):
        #issue is a ticket obj.
        self.redmine.issue.update(issue.id, **kwargs)

    def reply_to_issue(self, issue, notes=''):
        # reply to issue with specific note
        self.set_issue_property(issue, notes=notes)

