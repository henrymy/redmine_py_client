#!/usr/bin/env python
# -*- coding: utf-8 -*-

import argparse
import base64
import csv
from datetime import datetime, timedelta
import os
import yaml

from redminelib import exceptions as redmine_exceptions

import base
import utils

parser = argparse.ArgumentParser()
parser.add_argument('--ticket-csv', help='full path of input file in csv contains issues info.')
parser.add_argument('--expire-days', type=int,
                    default=14, help='number of days after which issue becomes staled(defualt:14).')
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

# status name for stale check
stale_status_list = (config['stale-check']['tenant'], config['stale-check']['tenant-vender'])

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

def get_issue_info_from_csv(record):
    if not record:
        return None
    issue_record = {}
    issue_record['id'] = record[0]
    issue_record['status'] = record[1]
    issue_record['ckkb_step_value'] = record[2]
    issue_record['subject'] = record[3]
    issue_record['project'] = record[4]
    issue_record['skill_code'] = record[5]
    issue_record['skill_name'] = record[6]
    issue_record['user_name'] = record[7]
    issue_record['priority'] = record[8]
    issue_record['update_count'] = record[9]
    issue_record['created_on'] = record[10]
    issue_record['init_action_date'] = record[11]
    issue_record['updated_on'] = record[12]
    issue_record['related_issues_str'] = record[13]

    return issue_record
    
def get_issue_stale_days(issue_record):
    if not issue_record:
        return None
    if issue_record['status'] in stale_status_list:
        updated_on = datetime.strptime(issue_record['updated_on'],'%Y-%m-%d %H:%M:%S')
        eclapsed = datetime.today() - updated_on 
        return eclapsed.days
    
with open(args.ticket_csv, 'r') as csv_file:
    reader = csv.reader(csv_file, quotechar='"', delimiter=',',
               quoting=csv.QUOTE_ALL)
    for line in reader:
        issue_record = get_issue_info_from_csv(line)
        stale_days = get_issue_stale_days(issue_record)
        if stale_days is not None and stale_days >= args.expire_days:
            print("#%s %s は %s 状態で %d 日放置されている。%s の担当者 %s に連絡してください." %
                (issue_record['id'], issue_record['subject'], issue_record['status'], stale_days,
                 issue_record['ckkb_step_value'], issue_record['user_name']))

print ("Check for stale tickets completed.")

"""
available properties of issue object:
'assigned_to', 'attachments', 'author', 'changesets', 'children', 'created_on', 'custom_fields', 'description', 'done_ratio', 'id', 'journals', 'priority', 'project', 'relations', 'status', 'subject', 'time_entries', 'tracker', 'updated_on', 'watchers'
"""
