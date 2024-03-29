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

issue_id = '86008'
#issue_id = '93647'
issue = redmine.get_issue_by_id(issue_id)
print(issue)
print('更新回数： %d' % len(issue.journals))
print('関連チケット：')
related_issues = redmine.get_issue_related_issues_str(issue)
print(related_issues)
"""
status_history = redmine.get_issue_status_history(issue)
print('ステータス変更履歴：')
print(status_history)
"""
init_act = redmine.get_issue_init_action_date(issue)
print('初動日時： %s' % init_act)
"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
