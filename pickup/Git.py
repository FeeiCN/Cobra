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
import subprocess


class Git:
    git = '/usr/bin/git'

    def __init__(self, filename, current_version=None, online_version=None):
        self.filename = filename
        self.current_version = current_version
        self.online_version = online_version

    def diff(self):
        svn_diff = subprocess.Popen(
            [self.git, 'diff', '-r', self.current_version + ':' + self.online_version, self.filename],
            stdout=subprocess.PIPE).communicate()[0]

        added, removed, changed = [], [], []
        diff = {}
        for line in svn_diff.split("\n"):
            if line[:3] in ('---', '+++', '==='):
                continue
            else:
                if len(line) > 0:
                    diff.setdefault(line[0], []).append(line[1:].strip())
                    if line[0] == '-':
                        removed.append(line[1:].strip())
                    elif line[0] == '+':
                        added.append(line[1:].strip())
                    elif line[0] == ' ':
                        changed.append(line[1:].strip())
                    else:
                        continue
        diff['code'] = svn_diff
        return diff
