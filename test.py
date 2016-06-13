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

import unittest
from engine import static
from pickup import subversion, GitTools, directory


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
        g = git.Git(filename, '123', '124')
        git_diff = g.diff()
        print(git_diff)

    def test_git(self):
        self.assertEqual('Test'.upper(), 'TEST')

    def test_directory(self):
        d = directory.Directory(self.project)
        d.collect_files()

    def test_static_analyse(self):
        s = static.Static('php', ['php'])
        s.analyse()


if __name__ == '__main__':
    unittest.main()
