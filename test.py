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

import time
import unittest
from engine import static
from pickup import subversion, GitTools, directory
from app import db, CobraAdminUser


class Test(unittest.TestCase):
    project = '/Volumes/Statics/Project/Company/mogujie'

    def test_svn_log(self):
        filename = self.project + '/appbeta/classes/controller/safe/admin.php'
        svn = subversion.Subversion(filename)
        svn.log()
        self.assertEqual('foo'.upper(), 'FOO')

    def test_svn_diff(self):
        filename = self.project + '/appbeta/classes/controller/safe/admin.php'
        svn = subversion.Subversion(filename, 'r717849', 'r718083')
        diff = svn.diff()
        # Print Result
        for event, values in diff.iteritems():
            print('{0} : {1}'.format(event, len(values)))

    def test_git_diff(self):
        filename = 'test.php'
        g = GitTools.Git(filename)
        git_diff = g.diff('123', '124')
        print(git_diff)

    def test_git(self):
        self.assertEqual('Test'.upper(), 'TEST')

    def test_directory(self):
        d = directory.Directory(self.project)
        d.collect_files()

    def test_static_analyse(self):
        s = static.Static('php', ['php'])
        s.analyse()

    def test_add_admin(self):
        username = 'admin'
        password = 'admin123456!@#'
        role = 1  # 1: super admin, 2: admin, 3: rules admin
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        au = CobraAdminUser(username, password, role, None, None, current_time, current_time)
        db.session.add(au)
        db.session.commit()


if __name__ == '__main__':
    unittest.main()
