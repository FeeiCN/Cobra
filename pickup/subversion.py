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


class Subversion:
    """Subversion Utility Class"""
    svn = '/usr/bin/svn'

    def __init__(self, filename, current_version=None, online_version=None):
        self.filename = filename
        self.current_version = current_version
        self.online_version = online_version

    def log(self):
        svn_log = subprocess.Popen(
            [self.svn, 'log', self.filename],
            stdout=subprocess.PIPE).communicate()[0]
        return svn_log

    def diff(self):
        svn_diff = subprocess.Popen(
            [self.svn, 'diff', '-r', self.current_version + ':' + self.online_version, self.filename],
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
