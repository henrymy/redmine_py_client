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

redmine = base.RedmineAPIClient(REDMINE_URL, API_KEY)

# get parent project
parent_prj = redmine.get_prj_by_id(PARENT_PRJ_ID)
# get tenant projects
sub_prj_list = redmine.get_sub_prj_list(parent_prj)

# get all open issues from each project
print("Collecting open tickets from following projects...")
open_issues = []
for prj in sub_prj_list:
    print(prj.name)
    prj_open_issues = redmine.get_issues_by_prj_and_status_id(prj, 'open')
    try:
        for issue in prj_open_issues:
            open_issues.append(issue)
    # not permitted to see tickes
    except redmine_exceptions.ForbiddenError:
        pass

print("Finished collecting open tickets.")
print("Total open ticket number: %s" % len(open_issues))
print("-" * 10)
issue = open_issues[0]
redmine.reply_to_issue(issue, notes='Hello ticket')

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
