#!/usr/bin/env python
# -*- coding: utf-8 -*- 
import base64
from datetime import date, datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import os
import smtplib
import yaml

from redminelib import Redmine
from redminelib import exceptions as redmine_exceptions

import utils

class RedmineAPIClient:
    redmine = None

    def __init__(self, url, api_key):
        self.redmine = Redmine(url, key=api_key)

    # return user obj of current user making request
    def get_current_user(self):
        return self.redmine.user.get('current')

    # get all projects
    def get_all_prj(self):
        projects = self.redmine.project.all()
        return projects

    # get project by project id
    def get_prj_by_id(self, project_id):
        return self.redmine.project.get(project_id)

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

    # get status obj by id 
    def get_status_by_id(self, status_id):
        #return self.redmine.issue_status.get(int(status_id))
        return self.redmine.issue_status.get(status_id)

    # get issue detail by issue id
    def get_issue_by_id(self, issue_id):
        issue_obj = self.redmine.issue.get(issue_id, include=['journals','relations'])
        return issue_obj

    # get issue detail by issue id light type
    def get_issue_by_id_lite(self, issue_id):
        issue_obj = self.redmine.issue.get(issue_id)
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

    # get issues in project filtered created after certain date
    def get_issues_by_prj_created_after_someday(self, project, status_id, created_on):
        query_date_str = ">=" + created_on 
        issues = self.redmine.issue.filter(
            project_id=project.id, status_id=status_id, created_on=query_date_str)
        return issues

    # get issues in project filtered updated after certain date
    def get_issues_by_prj_and_status_after_someday(self, project, status_id, update_date):
        query_date_str = ">=" + update_date
        issues = self.redmine.issue.filter(
            project_id=project.id, status_id=status_id, updated_on=query_date_str)
        return issues

    # get issues in project filtered status and date interval
    # without start_date or end_date recent 30-days tickets in status will be returned
    def get_issues_by_prj_and_status_between_somedays(self, project, status_id, start_date=None, end_date=None):
        if start_date is None or end_date is None:
            end_date = datetime.now().strftime('%Y-%m-%d')
            last_30_days = datetime.now() - timedelta(30)
            start_date = last_30_days.strftime('%Y-%m-%d')
        query_date_str = "><" + start_date + "|" + end_date
        issues = self.redmine.issue.filter(
            project_id=project.id, status_id=status_id, updated_on=query_date_str)
        return issues

    # get issues from list of projects with status and date interval
    # return a list of issues id
    def get_issues_from_projects_with_status_between_somedays(
        self,
        projects,
        status_id,
        start_date=None, end_date=None):
        status_issues = []
        for prj in projects:
            prj_status_issues = self.get_issues_by_prj_and_status_between_somedays(
                prj, status_id, start_date, end_date)
            try:
                for issue in prj_status_issues:
                    status_issues.append(issue)
            # not permitted to see tickes
            except redmine_exceptions.ForbiddenError:
                pass
        return status_issues
 
    # get all user obj
    def get_all_user(self):
        all_users = self.redmine.user.all()
        return user_obj
        
    # get user obj by user id
    def get_user_by_id(self, user_id):
        user_obj = self.redmine.user.get(int(user_id))
        return user_obj
        
    def get_issue_custom_fields(self, issue):
        custom_fields = getattr(issue,'custom_fields', None)
        if custom_fields:
            return custom_fields
        return []

    # get issue related issues
    # input para: issue object
    # return value: list of issue objs, return empty list if no related issues exist
    def get_issue_related_issues(self, issue):
        related_issue_list = []
        try:
            for related in issue.relations:
                related_issue = self.get_issue_by_id_lite(related.issue_id)
                related_issue_list.append(related_issue)
        # no relation issue exists
        except redmine_exceptions.ForbiddenError:
            pass
        return related_issue_list

    # get issue related issues in string format
    # input para: issue object
    # return value: return empty str if no related issues exist
    def get_issue_related_issues_str(self, issue, delimiter=';'):
        issues_str = ''
        issues_list = self.get_issue_related_issues(issue)
        if not issues_list:
            return issues_str
        issue_info_list = []
        for issue in issues_list:
            issue_info = str(issue.id) + ' ' + issue.subject
            issue_info_list.append(issue_info)
        issues_str = delimiter.join(issue_info_list)
        return issues_str

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

    # get issue custom field change history from journal
    # input para: issue object, cf_id str
    # return value: list of custom field value and datetime obj of timestamp
    def get_issue_cf_history(self, issue, cf_id):
        cf_history = []
        for journal in issue.journals:
            for detail in journal.details:
                if detail['property'] == 'cf' and detail['name'] == cf_id:
                    cf_history.append(
                        {'updated_on':journal['created_on'],
                        'cf_value':detail['new_value']})
                    continue
        return cf_history

    # get issue status change history from journal
    # input para: issue object
    # return value: list of status obj and datetime object of timestamp
    def get_issue_status_history(self, issue):
        status_history = []
        for journal in issue.journals:
            if journal.details == []:
                continue
            for detail in journal.details:
                if detail['property'] == 'attr' and detail['name'] == 'status_id':
                    old_status = self.get_status_by_id(int(detail['old_value']))
                    new_status = self.get_status_by_id(int(detail['new_value']))
                    status_history.append(
                        {'updated_on':journal['created_on'],
                        'old_status':old_status,
                        'new_status':new_status})
                    continue
        return status_history

    # get issue initial action date from journal
    # input para: issue object
    # return value: datetime object of timestamp
    def get_issue_init_action_date(self, issue):
        status_history = self.get_issue_status_history(issue)
        if status_history == []:
            return None
        for status in status_history:
            if status['new_status'].id == 31 or status['new_status'].id == 42:
                return status['updated_on']

    # get issue assigned change history from journal
    # input para: issue object
    # return value: list of assigned user obj and datetime object of timestamp
    def get_issue_assigned_history(self, issue):
        assigned_history = []
        for journal in issue.journals:
            for detail in journal.details:
                if detail['property'] == 'attr' and detail['name'] == 'assigned_to_id':
                    if 'new_value' in detail:
                        user_id = detail['new_value']
                        try:
                            user = self.get_user_by_id(user_id)
                        except redmine_exceptions.ResourceNotFoundError:
                            user = user_id
                    else:
                        user = ''
                    assigned_history.append(
                        {'updated_on':journal['created_on'],
                        'assigned_to':user})
                    continue
        return assigned_history

    # get issue reply count with: timestamp, user and charactor count
    # input para: issue object
    # return value: dict of reply count for each user
    def get_issue_reply_history_from_journal(self, issue):
        user_reply_dict = {}
        # build user -> reply dictionary
        for journal in issue.journals:
            timestamp = journal.created_on
            user_id = journal.user.id
            try:
                notes = journal.notes
            except redmine_exceptions.ResourceAttrError:
                notes = ''
            if user_id not in user_reply_dict:
                user_reply_dict[user_id] = {'summary':{},'details':[]}
            user_reply_dict[user_id]['details'].append(
                {'timestamp':timestamp,
                 'notes':notes})
        # calculate summary for each user
        for user_id in user_reply_dict.keys():
            details = user_reply_dict[user_id]['details']
            count = len(details)
            char_count = 0
            for detail in details:
                char_count = char_count + len(detail['notes'])
            average_chars = char_count/count
            summary = {'count':count, 'average_chars':average_chars}
            user_reply_dict[user_id]['summary'] = summary
            
        return user_reply_dict

    # if user have replied to an issue
    def get_issue_reply_history_for_user(self, user, issue):
        user_reply_dict = self.get_issue_reply_history_from_journal(issue)
        reply_of_user = {'summary':{},'details':[]}
        if user.id in user_reply_dict:
            details = user_reply_dict[user.id]
            reply_of_user['details'] = details
            count = len(details)
            char_count = 0
            for detail in details:
                char_count = char_count + len(detail['notes'])
            average_chars = char_count/count
            summary = {'count':count, 'average_chars':average_chars}
            reply_of_user['summary'] = summary
            return reply_of_user
        return None

    # get tickets working by certain user_id 
    def if_working_by_user(self, issue, user_id):
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
        user_id_hit = self.issue_assigned_to_user_list(issue, user_ids)
        if user_id_hit:
            return user_id_hit
        # 2nd: if currently not assigned, check journals too
        user_id_hit = self.issue_ever_assigned_to_user_list(issue, user_ids)
        if user_id_hit:
            return user_id_hit
        return False

    # check an issue is assigned to certain user_id
    def issue_assigned_to_user(self, issue, user_id):
        assigned_to = getattr(issue, 'assigned_to', None)
        if not assigned_to:
            return False 
        if assigned_to.id == user_id:
            return True
        return False 
        
    # check an issue is assigned to certain user list
    # input para1: issue obj
    # input para2: list of user ids
    # return the user_id after hit first user_id
    def issue_assigned_to_user_list(self, issue, user_ids):
        assigned_to = getattr(issue, 'assigned_to', None)
        if not assigned_to:
            return False 
        if assigned_to.id in user_ids:
            return assigned_to.id
        return False 

    # check an issue has ever been assigned_to certain user
    # contidion: new value of assigned_to_id property in journal.details == user.id
    def issue_ever_assigned_to_user(self, issue, user_id):
        for journal in reversed(issue.journals):
            check_this_id = journal.user.id
            journal_notes = getattr(journal, 'notes', '')
            try:
                if check_this_id == user_id and journal_notes != '':
                    return check_this_id
            except redmine_exceptions.ResourceAttrError:
                pass
        return False 

    # check an issue has ever been assigned_to certain user list
    # contidion: new value of assigned_to_id property in journal.details in user_ids
    def issue_ever_assigned_to_user_list(self, issue, user_ids):
        for journal in reversed(issue.journals):
            check_this_id = journal.user.id
            journal_notes = getattr(journal, 'notes', '')
            try:
                if check_this_id in user_ids and journal_notes != '':
                    return check_this_id
            except redmine_exceptions.ResourceAttrError:
                pass
        return False 

    # get issue life time
    # the lifetime of an issue is the interval between created_on and updated_on
    def get_issue_life_time(self, issue):
        pass
        
    # get all issues assigned to certain user
    def get_issues_assigned_to(self, user):
        # build a dict with user_id as keys to calculate number of working tickets
        pass

    # issue is a ticket obj.
    # set multi properties at same time.
    # e.g. assigned_to_id=<user id>, notes='some message'
    # e.g. custom_fields=[{'id': 1, 'value': 'foo'}]
    def set_issue_property(self, issue, **kwargs):
        self.redmine.issue.update(issue.id, **kwargs)

    def set_issue_assigned_to(self, issue, user_id=None):
        # set issue assigned_to with specific user id
        self.set_issue_property(issue, assigned_to_id=user_id)

    def reply_to_issue(self, issue, notes=''):
        # reply to issue with specific note
        self.set_issue_property(issue, notes=notes)

    # generate ticket report for some date interval
    def generate_report(self, start_date, end_date, projects, status_id, user_id_list):
        try:
            status = self.get_status_by_id(status_id)
            status_name = status.name 
        except redmine_exceptions.ResourceNotFoundError:
            status_name = status_id
        status_issues = []
        print("Collecting tickets from %s to %s ..." % (start_date, end_date))
        status_issues = self.get_issues_from_projects_with_status_between_somedays(
            projects,
            status_id,
            start_date,
            end_date)
        print("From %s to %s: Total %s ticket number is %d" % ( 
            start_date, end_date, status_name, len(status_issues)))

        # build a dict with user_id as keys to calculate number of working tickets
        working_by_user={}
        for user_id in user_id_list:
            working_by_user[user_id] = 0

        # loop all ticket and add to each user id
        for issue in status_issues:
            issue_obj = self.get_issue_by_id(issue.id)
       #     print("%d: %s" % (issue.id, issue.subject))
       #     print('Check if working by users in users_dict...')
            check_this_id = self.if_working_by_user_list(issue, user_id_list)
            if check_this_id:
                working_by_user[check_this_id] += 1

        print("Total %s tickets for each user:" % status_name)
        print("-" * 10)
        for user_id in user_id_list:
            user = self.get_user_by_id(user_id)
            print("%s %s: %s" % (user.lastname, user.firstname, working_by_user[user.id]))
        print("-" * 10)

