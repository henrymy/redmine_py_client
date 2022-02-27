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

# get parent project
parent_prj = redmine.get_prj_by_id(PARENT_PRJ_ID)
# get tenant projects
sub_prj_list = redmine.get_sub_prj_list(parent_prj)

# get all ticket updated last day
print("Collecting all tickets changed yesterday from following projects...")
updated_issues = []
old_status_id = 'open'
new_status_id = 'closed'
yesterday = datetime.now() - timedelta(1)
date_yesterday = datetime.strftime(yesterday, '%Y-%m-%d')
date_yesterday = '2022-02-24'

for prj in sub_prj_list:
    print(prj.name)
    prj_updated_issues = redmine.get_updated_issues_by_prj_and_status(prj, new_status_id, date_yesterday)
    try:
        for issue in prj_updated_issues:
            updated_issues.append(issue)
    # not permitted to see tickes
    except redmine_exceptions.ForbiddenError:
        pass

print("Finished collecting updated tickets.")
print("Total updated ticket number: %s" % len(updated_issues))
print("-" * 10)

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
