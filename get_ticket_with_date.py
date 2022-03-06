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
PRJ_KW = config['redmine']['project_kw']
PRJ_NOT_KW1 = config['redmine']['project_not_kw1']
DEV_MEMS = config['dev_members']
MAIL_SERVER = config['mailserver']['name']
PORT = config['mailserver']['port']
FROM = config['address']['from']
TO = config['address']['to']

DEBUG = config['debug']['trace']
if DEBUG:
    MAIL_SERVER = 'localhost'
    PORT = 8025
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

# get parent project
parent_prj = redmine.get_prj_by_id(PARENT_PRJ_ID)
# get tenant projects
sub_prj_list = redmine.get_sub_prj_list(parent_prj)

# get all issues from each project
print("Collecting tickets from following projects...")
open_issues = []
closed_issues = []
end_date = datetime.now().strftime('%Y-%m-%d')
last_30_days = datetime.now() - timedelta(30)
start_date = last_30_days.strftime('%Y-%m-%d')
for prj in sub_prj_list:
    print(prj.name)
    prj_open_issues = redmine.get_issues_by_prj_and_status_between_somedays(
        prj,
        'open',
        start_date,
        end_date)
    prj_closed_issues = redmine.get_issues_by_prj_and_status_between_somedays(
        prj,
        'closed',
        start_date,
        end_date)
    try:
        for issue in prj_open_issues:
            open_issues.append(issue)
        for issue in prj_closed_issues:
            closed_issues.append(issue)
    # not permitted to see tickes
    except redmine_exceptions.ForbiddenError:
        pass

print("Finished collecting tickets.")
print("Total open ticket number: %s" % len(open_issues))
print("Total closed ticket number: %s" % len(closed_issues))
# define dev members here
dev_members = DEV_MEMS
"""
dev_members = [
    {'user_name': '染谷 諭司', 'user_id': '6354'},
    {'user_name': '張 鵬', 'user_id': '5883'},
    {'user_name': '内海 卓也', 'user_id': '1831'}
]
"""
# build a dict with user_id as keys to calculate number of working tickets
working_by_user={}
for dev_mem in dev_members:
    user_id = dev_mem['user_id']
    # get user object
    user_obj = redmine.get_user_by_id(user_id)
    working_by_user[user_id] = 0
print(working_by_user)
# loop all ticket and add to each user id
"""
# use for test single ticket only
test_issue_id = '83273'
# get issue object
test_issue_obj = redmine.get_issue_by_id(test_issue_id)
test_issues = [test_issue_obj]
for issue in test_issues:
"""
for issue in closed_issues:
    issue_obj = redmine.get_issue_by_id(issue.id)
    print(issue)
    print('Check if assigned_to dev_members...')
    check_this_id =''
    # 1st: check assigned_to property
    if getattr(issue_obj, 'assigned_to', False):
        check_this_id = issue_obj.assigned_to.id
        if check_this_id in working_by_user:
            print("Catch One in assigned_to!")
            print(check_this_id)
            working_by_user[check_this_id] += 1
            continue
    # 2nd: if not assigned_to dev_member, check journals too
    # contidion: edited by dev_mem and journal.note is not empty
    print('Check if edited by dev_members...')
    for journal in issue_obj.journals:
        check_this_id = journal.user.id
        journal_notes = getattr(journal, 'notes', '')
        if check_this_id in working_by_user and journal_notes != '':
            print("Catch One in issue journals!")
            print(check_this_id)
            working_by_user[check_this_id] += 1
            break
print("Total working tickets for each dev members:")
print("-" * 10)
for dev_mem in dev_members:
    user_id = dev_mem['user_id']
    user_name = dev_mem['user_name']
    working_tickets = working_by_user[user_id]
    print("%s:%s" % (user_name, working_tickets))
print("-" * 10)

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
