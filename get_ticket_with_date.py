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
# define start_date and end_date with yyyy-mm-dd format
end_date = datetime.now().strftime('%Y-%m-%d')
last_30_days = datetime.now() - timedelta(30)
start_date = last_30_days.strftime('%Y-%m-%d')
# open and closed are special status_ids which do not have status objects
status_id = 'closed'
# call generate_report method
redmine.generate_report(start_date, end_date, sub_prj_list, status_id, user_id_list)

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
