#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from datetime import datetime, timedelta
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import os
import smtplib
import yaml

from redminelib import exceptions as redmine_exceptions

import base
import utils

LOCAL_PATH = os.getcwd()
LOCAL_PATH += '/'
CONFIG_FILE_NAME = 'config.yml'
config = utils.load_conf(LOCAL_PATH, CONFIG_FILE_NAME)

REDMINE_URL = config['redmine']['url']
API_KEY = config['redmine']['api_key']
PARENT_PRJ_ID = config['redmine']['parent_prj_id']
DEV_MEMS = config['dev_members']

DEBUG = config['debug']['trace']
if DEBUG:
    import pdb
    pdb.set_trace()

FAKE_ISSUES = config['debug']['fake_issues']
if FAKE_ISSUES:
    import test.fake_issues
    issues = test.fake_issues.get_fake_issues()
else:
    redmine = base.RedmineAPIClient(REDMINE_URL, API_KEY)

# get current user who is using this api-key
myself = redmine.get_current_user()

# define dev members here
dev_members = DEV_MEMS

# get parent project
parent_prj = redmine.get_prj_by_id(PARENT_PRJ_ID)
# get tenant projects
sub_prj_list = redmine.get_sub_prj_list(parent_prj)

# build a list with user_id to calculate number of working tickets
user_id_list = []
for dev_mem in dev_members:
    user_id_list.append(dev_mem['user_id'])
end_date = datetime.now().strftime('%Y-%m-%d')
last_30_days = datetime.now() - timedelta(30)
start_date = last_30_days.strftime('%Y-%m-%d')
status_id = 'closed'
redmine.generate_report(start_date, end_date, sub_prj_list, status_id, user_id_list)

"""
# build a dict with user_id as keys to calculate number of working tickets
working_by_user={}
for dev_mem in dev_members:
    user_id = dev_mem['user_id']
    # get user object
    user_obj = redmine.get_user_by_id(user_id)
    working_by_user[user_id] = 0
print(working_by_user)
# get all issues from each project
print("Collecting tickets from all sub projects...")
status_issues = []
print("Collecting tickets last 30 days...")
end_date = datetime.now().strftime('%Y-%m-%d')
last_30_days = datetime.now() - timedelta(30)
start_date = last_30_days.strftime('%Y-%m-%d')
status_id = 'open'
status_issues = redmine.get_issues_from_projects_with_status_between_somedays(
    sub_prj_list,
    'open',
    start_date,
    end_date)
print("From %s to %s: Total %s ticket number is %d" % (
    start_date, end_date, status_id, len(status_issues)))

status_id = 'closed'
closed_issues = redmine.get_issues_from_projects_with_status_between_somedays(
    sub_prj_list,
    'closed',
    start_date,
    end_date)
print("From %s to %s: Total %s ticket number is %d" % (
    start_date, end_date, status_id, len(status_issues)))

# loop all ticket and add to each user id
for issue in closed_issues:
    issue_obj = redmine.get_issue_by_id(issue.id)
    print(issue)
    print('Check if working by dev_members...')
    check_this_id = redmine.if_working_by_user_list(issue, working_by_user.keys())
    if check_this_id:
        working_by_user[check_this_id] += 1
        
print("Total working tickets for each dev members:")
print("-" * 10)
for dev_mem in dev_members:
    user_id = dev_mem['user_id']
    user_name = dev_mem['user_name']
    working_tickets = working_by_user[user_id]
    print("%s:%s" % (user_name, working_tickets))
print("-" * 10)

"""
"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
