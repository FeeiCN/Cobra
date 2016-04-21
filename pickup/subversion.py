#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
from utils import common
import sys, subprocess, re, os
from collections import defaultdict


def log(filename):
    reader = os.popen('/usr/bin/svn log ' + filename)
    log_list = reader.read()
    reader.close()
    return log_list


def diff(filename, current_version, online_version):
    svn_diff = subprocess.Popen(['/usr/bin/svn', 'diff', '-r', current_version + ':' + online_version, filename],
                                stdout=subprocess.PIPE).communicate()[0]

    added, removed, changed = [], [], []
    for line in svn_diff.split("\n"):
        if line[:3] in ('---', '+++', '==='):
            continue
        else:
            if len(line) > 0:
                if line[0] == '-':
                    removed.append(line[1:].strip())
                elif line[0] == '+':
                    added.append(line[1:].strip())
                elif line[0] == ' ':
                    changed.append(line[1:].strip())
                else:
                    continue

    print added
