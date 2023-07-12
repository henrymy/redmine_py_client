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

groups = redmine.redmine.group.all()
for grp in groups:
    for user in grp.users:
        print(','.join([grp.name, user.name]))

"""
prj_id ='651'
prj = redmine.get_prj_by_id(prj_id)
available properties of project object:
'created_on', 'description', 'enabled_modules', 'files', 'id', 'identifier', 'issue_categories', 'issues', 'memberships', 'name', 'news', 'status', 'time_entries', 'time_entry_activities', 'trackers', 'updated_on', 'versions', 'wiki_pages'

available properties of membership object:
'group', 'id', 'project', 'roles'
or
'group', 'id', 'project', 'user'
"""
