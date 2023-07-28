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

#issue_id = '86008'
issue_id = '88436'
issue = redmine.get_issue_by_id(issue_id)
print("タイトル: %s" % issue.subject)
print("作成日時: %s" % issue.created_on)
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

today = date.today()
updated_on = issue.updated_on.date()
elapsed = today - updated_on
print('最後アップデート日からの経過日数： %s' % elapsed.days)

# 保留中と終了は除外
open_status_set = (1,30,31,41,42,60,63)
if (issue.status.id in open_status_set) and (elapsed.days >= 14):
    print("%s : %s は放置されています." % (issue.id, issue.status.name))

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'

valid status id:
1 新規／未着手
5 終了
30 サービスデスク対応中
31 テナント対応中
41 開発担当者対応中
42 テナントベンダー対応中
60 開発担当者（J）対応中
63 運用担当者対応中
64 保留中
"""
