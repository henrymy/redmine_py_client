#!/usr/bin/env python
# -*- coding: utf-8 -*-

import base64
from datetime import date, timedelta
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import smtplib
import yaml

from redminelib import Redmine, exceptions

with open('config.yml', 'r') as f:
    config = yaml.safe_load(f)

REDMINE_URL = config['redmine']['url']
API_KEY = config['redmine']['api_key']
PRJ_ID = config['redmine']['project_id']
MAIL_SERVER = config['mailserver']['name']
PORT = config['mailserver']['port']
FROM = config['address']['from']
TO = config['address']['to']

DEBUG = config['debug']['trace']
if DEBUG:
    import pdb
    pdb.set_trace()
    MAIL_SERVER = 'localhost'
    PORT = 8025

FAKE_ISSUES = config['debug']['fake_issues']
if FAKE_ISSUES:
    import test.fake_issues
    issues = test.fake_issues.get_fake_issues()
else:
    redmine = Redmine(REDMINE_URL, key=API_KEY)
    issues = redmine.issue.filter(project_id=PRJ_ID, sort='due_date:desc')

today = date.today()
yesterday = today - timedelta(days=1)
with open('saved_data.yml', 'r') as f:
    saved_data = yaml.safe_load(f)

delayed_issues = []
until_today_issues = []
due_unknown_issues = []
MIN_LEN = 5
for issue in issues:
    issue_info = ''
    assigned_to_str = str(issue.assigned_to)
    if len(assigned_to_str) < MIN_LEN:
        assigned_to_str += '    '
    try:
        getattr(issue, 'due_date')
        issue_info = '\t'.join(
            [str(issue.id),
             str(issue.due_date),
             assigned_to_str,
             issue.subject
            ])
    except exceptions.ResourceAttrError:
        issue_info = '\t'.join(
            [str(issue.id),
             u'---未設定---',
             assigned_to_str,
             issue.subject
            ])
        due_unknown_issues.append(issue_info)
        continue
    if issue.due_date == today:
        until_today_issues.append(issue_info)
    if issue.due_date < today:
        delayed_issues.append(issue_info)

total = len(due_unknown_issues) + len(delayed_issues)
diff = total - saved_data['sum_yesterday']
if diff >= 0:
    sign = '+'
else:
    sign = '-'

main_text = ""
HELLO = (u'お疲れ様です。チケット状況の自動配信を行います。\n'
          '本日期限または期限超過の未完了チケットについて連絡します。\n'
          '各チームにて、期限通りの完了をお願いします。\n')
main_text += HELLO
SUM = u"現在期限超過(未設定も含む)チケットの件数は:{0}\n".format(total)
DIFF = u"前日との差分は: {0}{1}\n".format(sign, abs(diff))
main_text += SUM
main_text += DIFF
main_text += u'--------本日までのチケット一覧--------\n'
main_text += u'--ID--  ----期限----  ----担当----      ----題名----\n'
for line in until_today_issues:
    main_text += line
    main_text += '\n'
main_text += u'---------------------------------------\n'

main_text += u'--------期限切れ(未設定も含む)のチケット一覧--------\n'
main_text += u'--ID--  ----期限----  ----担当----      ----題名----\n'
for line in delayed_issues:
    main_text += line
    main_text += '\n'
for line in due_unknown_issues:
    main_text += line
    main_text += '\n'
main_text += u'---------------------------------------\n'

charset = "utf-8"
msg = MIMEText(main_text, "plain", charset)
msg.replace_header("Content-Transfer-Encoding", "base64")
msg["Subject"] = u"{0}/{1}/{2}: チケットレポート自動送信".format(
    today.year, today.month, today.day)
msg["From"] = FROM
msg["To"] = TO
msg["Cc"] = ""
msg["Bcc"] = ""
msg["Date"] = formatdate(None,True)

server = smtplib.SMTP(MAIL_SERVER, PORT)
server.set_debuglevel(1)
server.send_message(msg)
server.quit()

with open('saved_data.yml', 'w') as f:
    data = {'sum_yesterday': total}
    f.write(yaml.dump(data, default_flow_style=False))
