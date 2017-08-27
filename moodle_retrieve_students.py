#!/usr/bin/python3
import sys
import re
import csv
import requests

base_url = 'https://ava.ead.ufscar.br'
student_role = 5

moodle_session = sys.argv[1]
course_id = int(sys.argv[2])
students_csv = csv.reader(open(sys.argv[3]), delimiter=';')
out_csv = csv.writer(sys.stdout, delimiter=';')

students = {}
for sid, name in students_csv:
    students[name.lower()] = (sid, name)

ses = requests.Session()
ses.cookies.set('MoodleSession', moodle_session)

r = ses.get(base_url +
            '/user/index.php?roleid=%d&id=%d&perpage=10000' % (
                student_role,
                course_id)
            )
r.raise_for_status()

for m in re.finditer(r'<a href="[^"]+/user/view\.php\?'
                     r'id=(\d+)[^"]*">([^<]+)</a>',
                     r.text):
    moodle_sid, name = m.groups()
    sid, name = students.get(name.lower(), (None, name))
    if not sid:
        sys.stderr.write('ERROR: student "%s" not found in the csv!\n'
                         % name)
        sys.exit(1)
    out_csv.writerow([sid, moodle_sid, name])
