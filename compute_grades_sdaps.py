#!/usr/bin/python3
import sys
import csv

score_config = sys.argv[1].strip().split()

writer = csv.writer(sys.stdout, delimiter=';')

for row in csv.DictReader(sys.stdin, delimiter=','):
    comments = ''
    for quest, col in row.items():
        if ';' in col:
            row[quest], comment = col.split(';', 2)
            comments += '[%s]: %s.\n\n' % (quest, comment)
    comments = comments.strip()

    stack = []
    for op in score_config:
        if op.startswith('<'):
            stack.append(float(row[op[1:]]))
        elif op == '==':
            stack.append(abs(stack.pop() - stack.pop()) <= 0.01)
        elif op == '*':
            stack.append(stack.pop() * stack.pop())
        elif op == '+':
            stack.append(stack.pop() + stack.pop())
        else:
            stack.append(float(op))
    assert(len(stack) == 1)

    grade = ('%.2f' % stack[0]).replace('.', ',')
    writer.writerow([row['questionnaire_id'], grade, comments])
