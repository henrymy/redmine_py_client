#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
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

parser = argparse.ArgumentParser()
parser.add_argument('--status-id', help='status_id to filter issues.')
parser.add_argument('--start-date', help='filter issues updated after this date.')
parser.add_argument('--end-date', help='filter issues updated before this date.')
args = parser.parse_args()

LOCAL_PATH = os.getcwd()
LOCAL_PATH += '/'
CONFIG_FILE_NAME = 'config.yml'
config = utils.load_conf(LOCAL_PATH, CONFIG_FILE_NAME)

REDMINE_URL = config['redmine']['url']
API_KEY = config['redmine']['api_key']
PARENT_PRJ_ID = config['redmine']['parent_prj_id']
# define user groups
TRAD_DEV_A = config['users']['trad-dev-A']
TRAD_DEV_B= config['users']['trad-dev-B']
JTP = config['users']['jtp']
SD = config['users']['sd']
OPS = config['users']['trad-ops']
GTY = config['users']['trad-gty']

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

# get parent project
parent_prj = redmine.get_prj_by_id(PARENT_PRJ_ID)
# get tenant projects
sub_prj_list = redmine.get_sub_prj_list(parent_prj)

# build a list with user_group to calculate number of working tickets
user_skill_code = {}
user_skill_name = {}
for mem in TRAD_DEV_A:
    if mem['user_id'] == 188:
        user_skill_code[mem['user_id']] = '"1001,9001"'
        user_skill_name[mem['user_id']] = '"上級開発者, 茂木"'
    if mem['user_id'] == 2370:
        user_skill_code[mem['user_id']] = '"1001,9002"'
        user_skill_name[mem['user_id']] = '"上級開発者, 前島"'
    if mem['user_id'] == 1831:
        user_skill_code[mem['user_id']] = '"1001,9003"'
        user_skill_name[mem['user_id']] = '"上級開発者, 内海"'
    if mem['user_id'] == 3335:
        user_skill_code[mem['user_id']] = '"1001,9004"'
        user_skill_name[mem['user_id']] = '"上級開発者, 鳥海"'
    if mem['user_id'] == 5883:
        user_skill_code[mem['user_id']] = '"1001,9005"'
        user_skill_name[mem['user_id']] = '"上級開発者, 張"'
    if mem['user_id'] == 6354:
        user_skill_code[mem['user_id']] = '"1001,9006"'
        user_skill_name[mem['user_id']] = '"上級開発者, 染谷"'
    if mem['user_id'] == 192:
        user_skill_code[mem['user_id']] = '"1001,9007"'
        user_skill_name[mem['user_id']] = '"上級開発者, 對間"'
    if mem['user_id'] == 248:
        user_skill_code[mem['user_id']] = '"1001,9008"'
        user_skill_name[mem['user_id']] = '"上級開発者, 田中"'
    if mem['user_id'] == 6550:
        user_skill_code[mem['user_id']] = '"1001,9009"'
        user_skill_name[mem['user_id']] = '"上級開発者, 杉田"'
for mem in TRAD_DEV_B:
    user_skill_code[mem['user_id']] = '1003'
    user_skill_name[mem['user_id']] = '一般開発者B'
for mem in JTP:
    user_skill_code[mem['user_id']] = '1002'
    user_skill_name[mem['user_id']] = '一般開発者A'
for mem in SD:
    user_skill_code[mem['user_id']] = '"1099,9101"'
    user_skill_name[mem['user_id']] = '"その他, SD"'
for mem in OPS:
    user_skill_code[mem['user_id']] = '"1099,9102"'
    user_skill_name[mem['user_id']] = '"その他, OPS"'
for mem in GTY:
    user_skill_code[mem['user_id']] = '"1099,9103"'
    user_skill_name[mem['user_id']] = '"その他,GANTRY"'

# build a list with user_id to calculate number of working tickets 
user_id_list = []
user_id_list_dev_and_sd = []
for mem in TRAD_DEV_A:
    user_id_list.append(mem['user_id'])
    user_id_list_dev_and_sd.append(mem['user_id'])
for mem in TRAD_DEV_B:
    user_id_list.append(mem['user_id'])
    user_id_list_dev_and_sd.append(mem['user_id'])
for mem in JTP:
    user_id_list.append(mem['user_id'])
    user_id_list_dev_and_sd.append(mem['user_id'])
for mem in SD:
    user_id_list.append(mem['user_id'])
    user_id_list_dev_and_sd.append(mem['user_id'])
for mem in OPS:
    user_id_list.append(mem['user_id'])
for mem in GTY:
    user_id_list.append(mem['user_id'])
# define start_date and end_date with yyyy-mm-dd format
end_date = args.end_date
start_date = args.start_date
# open and closed are special status_ids which do not have status objects
if not args.status_id:
    status_id = 'closed'
else:
    status_id = args.status_id
# call generate_report method
#redmine.generate_report(start_date, end_date, sub_prj_list, status_id, user_id_list)

# call generate_assign_report method
status_issues = redmine.get_issues_from_projects_with_status_between_somedays(
            sub_prj_list,
            status_id,
            start_date,
            end_date)

# user_id_list
# user_id_list_dev_and_sd
# user_skill_code
# user_skill_name
# helper to get user full name
def get_username(user_id):
    if user_id is False:
        return '-'
    user = redmine.get_user_by_id(check_this_id)
    return user.lastname + ' ' +  user.firstname

for issue in status_issues:
    issue = redmine.get_issue_by_id(issue.id)
    issue_work_group = ''
    ckkb_step = redmine.get_issue_step_info(issue)
    if ckkb_step is False:
        ckkb_step_value = '-'
    else:
        ckkb_step_value = ckkb_step.value
    update_count = len(issue.journals)
    init_action_date = redmine.get_issue_init_action_date(issue)
    related_issues_str = redmine.get_issue_related_issues_str(issue)
    # 1st: check ticket status for service desk
    if issue.status.id in [1, 30]:
        skill_code = '"1099,9101"'
        skill_name = '"その他, SD"'
        check_this_id = redmine.if_working_by_user_list(issue, user_id_list) 
        user_name = get_username(check_this_id)
        columns = [str(issue.id), str(issue.status), str(ckkb_step_value), issue.subject,
            str(issue.project), skill_code, skill_name, user_name, str(issue.priority),
            str(update_count),str(issue.created_on), 
            str(init_action_date),str(issue.updated_on),
            related_issues_str]
        print("%s" % ",".join(columns))
        continue
    # 2nd: check ticket ckkb-step for ops/gantry
    if ckkb_step_value in ['GANTRY','OPS']:
        check_this_id = redmine.if_working_by_user_list(issue, user_id_list) 
        skill_code = user_skill_code[check_this_id]
        skill_name = user_skill_name[check_this_id]
        user_name = get_username(check_this_id)
        columns = [str(issue.id), str(issue.status), str(ckkb_step_value), issue.subject,
            str(issue.project), skill_code, skill_name, user_name, str(issue.priority),
            str(update_count),str(issue.created_on), 
            str(init_action_date),str(issue.updated_on),
            related_issues_str]
        print("%s" % ",".join(columns))
        continue
    # 3rd: check other ticket for only dev and sd members
    check_this_id = redmine.if_working_by_user_list(issue, user_id_list_dev_and_sd) 
    skill_code = user_skill_code[check_this_id]
    skill_name = user_skill_name[check_this_id]
    user_name = get_username(check_this_id)
    columns = [str(issue.id), str(issue.status), str(ckkb_step_value), issue.subject,
        str(issue.project), skill_code, skill_name, user_name, str(issue.priority),
        str(update_count),str(issue.created_on), 
        str(init_action_date),str(issue.updated_on),
        related_issues_str]
    print("%s" % ",".join(columns))

    
"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
