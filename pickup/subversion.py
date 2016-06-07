#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import subprocess
import sys
import logging
import ConfigParser


class Subversion:
    """Subversion Utility Class"""
    svn = '/usr/bin/svn'

    def __init__(self, filename, current_version=None, online_version=None):
        self.filename = filename
        self.current_version = current_version
        self.online_version = online_version

        config = ConfigParser.ConfigParser()
        config.read('config')
        self.username = config.get('svn', 'username')
        self.password = config.get('svn', 'password')

        # Test SVN
        cmd = self.svn + " info --no-auth-cache --non-interactive --username='%s' --password='%s' %s" % (
            self.username,
            self.password,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (diff_out, diff_err) = p.communicate()
        if len(diff_err) == 0:
            logging.debug("svn diff success")
        elif 'authorization failed' in diff_err:
            logging.warning("svn diff auth failed")
            sys.exit(1)
        elif 'Not a valid URL' in diff_err:
            logging.warning("svn diff url not a valid")
            sys.exit(1)

    def log(self):
        cmd = self.svn + " log --no-auth-cache --non-interactive --username='%s' --password='%s' %s" % (
            self.username,
            self.password,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        log_out = p.communicate()[0]
        return log_out

    def diff(self):
        cmd = self.svn + " diff --no-auth-cache --non-interactive --username='%s' --password='%s' -r %s:%s %s" % (
            self.username,
            self.password,
            self.current_version,
            self.online_version,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        diff_out = p.communicate()[0]

        added, removed, changed = [], [], []
        diff = {}
        for line in diff_out.split("\n"):
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
        diff['code'] = diff_out
        return diff

    def commit(self):
        svn_log = subprocess.Popen(
            [self.svn, 'log', self.filename],
            stdout=subprocess.PIPE).communicate()[0]
        return svn_log
