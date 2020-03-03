from datetime import date
class FakeIssue:
    def __init__(self, assigned_to, due_date, id, subject):
        self.assigned_to = assigned_to 
        self.due_date = due_date
        self.id = id 
        self.subject = subject

fake_issue1 = FakeIssue(u'英雄太郎', date(2020,3,1), 101, u'基本設計書')
fake_issue2 = FakeIssue(u'英雄太郎', date(2020,3,2), 102, u'詳細設計書')
fake_issue3 = FakeIssue(u'英雄太郎', date(2020,3,3), 103, u'パラメータシート')
fake_issue4 = FakeIssue(u'英雄太郎', date(2020,3,3), 104, u'構築手順')
fake_issue5 = FakeIssue(u'英雄太郎', date(2020,3,5), 105, u'テスト項目')

fake_issues = [fake_issue1,
               fake_issue2,
               fake_issue3,
               fake_issue4,
               fake_issue5
              ]

def get_fake_issues():
    return fake_issues

