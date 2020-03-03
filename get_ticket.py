import pdb
import test.fake_issues

pdb.set_trace()
issues = test.fake_issues.get_fake_issues()
for issue in issues:
  print ('%d:%s:%s' % (issue.id, issue.due_date, issue.subject))
