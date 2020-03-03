import base64
from email.mime.text import MIMEText
from email.header import Header
from email.utils import formatdate
import smtplib

from redminelib import Redmine
from datetime import date, timedelta

from redminerc import REDMINE_URL,API_KEY,PRJ_ID,FROM

import test.fake_issues
import pdb

MAIL_SERVER = "localhost"
PORT=8025
TO_TEST = "zhang@mac.local"

redmine = Redmine(REDMINE_URL, key=API_KEY)
#issues = redmine.issue.filter(project_id=PRJ_ID)
issues = test.fake_issues.get_fake_issues()
today = date.today()
yesterday = today - timedelta(days=1)

pdb.set_trace()
delayed_issues = []
until_today_issues = []
for issue in issues:
    issue_info = ' '.join(
        [str(issue.id),
         issue.assigned_to,
         str(issue.due_date),
         issue.subject
        ])
    if issue.due_date == today:
        until_today_issues.append(issue_info)
    if issue.due_date < today:
        delayed_issues.append(issue_info)

total = len(until_today_issues) + len(delayed_issues)

main_text = ""
HELLO = (u'本日期限または期限超過の未完了チケットについて連絡します。\n'
          '各チームにて、期限通りの完了をお願いします。\n')
main_text += HELLO
SUM = u"現在期限超過チケットの件数は:{0}\n".format(len(delayed_issues))
main_text += SUM
main_text += u'--------本日までのチケット一覧--------'
main_text += '\n'
for line in until_today_issues:
    main_text += line
    main_text += '\n'
main_text += u'---------------------------------------'
main_text += '\n'

main_text += u'--------期限切れのチケット一覧--------'
main_text += '\n'
for line in delayed_issues:
    main_text += line
    main_text += '\n'
main_text += u'---------------------------------------'
main_text += '\n'

charset = "utf-8"
msg = MIMEText(main_text, "plain", charset)
msg.replace_header("Content-Transfer-Encoding", "base64")
msg["Subject"] = u"{0}/{1}/{2}: チケットレポート自動送信".format(
    today.year, today.month, today.day)
msg["From"] = FROM
msg["To"] = TO_TEST
msg["Cc"] = ""
msg["Bcc"] = ""
msg["Date"] = formatdate(None,True)

server = smtplib.SMTP(MAIL_SERVER, PORT)
server.set_debuglevel(1)
server.send_message(msg)
server.quit()
