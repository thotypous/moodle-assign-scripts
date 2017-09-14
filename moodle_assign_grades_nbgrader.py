#!/usr/bin/python3
import sys
import re
import os
import csv
import itertools
import requests

FORMAT_HTML = 1
FORMAT_PLAIN = 2

base_url = 'https://ava.ead.ufscar.br'
assignment_file_templ = '{}.html'
comment_format = FORMAT_PLAIN

moodle_session = sys.argv[1]
assign_id = int(sys.argv[2])
students_moodle_csv = csv.reader(open(sys.argv[3]), delimiter=';')

students = {}
for sid, moodle_sid, name in students_moodle_csv:
    students[moodle_sid] = sid

ses = requests.Session()
ses.cookies.set('MoodleSession', moodle_session)

rownum = 0

for rownum in itertools.count(start=0):
    r = ses.get(base_url +
                '/mod/assign/view.php?id=%d&rownum=%d&action=grade' % (
                    assign_id,
                    rownum)
                )
    r.raise_for_status()

    if 'Row is out of bounds for the current grading table' in r.text:
        break

    m = re.search(r'<a href="[^"]+/user/view\.php\?id=(\d+)[^"]*">([^<]+)</a>',
                  r.text)
    moodle_sid, name = m.groups()
    sid = students.get(moodle_sid)
    if not sid:
        sys.stderr.write('ERROR: student "%s" (id %s) not found in the csv! '
                         ' re-run moodle_retrieve_students.py\n'
                         % (name, moodle_sid))
        sys.exit(1)

    params = {}
    params_regex = [
        ('sesskey', r'"sesskey":"([^"]+)"'),
        ('client_id', r'"client_id":"([^"]+)"'),
        ('itemid', r'"itemid":(\d+)'),
        ('ctx_id', r'contextid=([^"]+)"'),
        ('repo_id', r'"recentrepository":"(\d+)"'),
    ]
    for param, regex in params_regex:
        m = re.search(regex, r.text)
        params[param] = m.group(1)

    file_info = {}
    assignment_file = assignment_file_templ.format(sid)
    grade = ''
    if os.path.exists(assignment_file):
        with open(assignment_file, 'r', encoding='utf-8') as f:
            m = re.search(r'<h4>[^<]+ \(Score: ([^ ]+)', f.read())
            if m:
                grade = m.group(1).replace('.', ',')
        print('-> %s (%s)' % (assignment_file, grade))
        with open(assignment_file, 'rb') as f:
            upload_params = params.copy()
            upload_params.update({
                'env': 'filemanager',
                'title': assignment_file,
                'author': name,
                'license': 'allrightsreserved',
            })
            r = ses.post(base_url +
                         '/repository/repository_ajax.php?action=upload',
                         files={'repo_upload_file': f},
                         data=upload_params)
            r.raise_for_status()
            file_info = r.json()

    grade_keys = {'sesskey', }
    grade_params = {k: v for k, v in params.items() if k in grade_keys}
    grade_params.update({
        'action': 'submitgrade',
        'savegrade': 'Save',
        'id': assign_id,
        'rownum': rownum,
        'assignfeedbackcomments_editor[text]': '',
        'assignfeedbackcomments_editor[format]': comment_format,
        'grade': grade,
    })
    grade_params['_qf__mod_assign_grade_form_%d' % rownum] = 1
    if 'id' in file_info:
        grade_params['files_%s_filemanager' % moodle_sid] = file_info['id']

    r = ses.post(base_url + '/mod/assign/view.php',
                 data=grade_params)
    r.raise_for_status()
