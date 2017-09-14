#!/usr/bin/python3
import re
import sys
import os
import shutil

for line in sys.stdin:
    if ',' in line:
        sidA, sidB = [re.search(r'^\s*(\d+)', x).group(1) for x in line.split(',')]
        fA, fB = sidA + '.html', sidB + '.html'
        if os.path.exists(fA):
            shutil.copy(fA, fB)
        elif os.path.exists(fB):
            shutil.copy(fB, fA)
        else:
            print('Neither %s nor %s found' % (fA, fB))
