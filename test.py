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

import unittest
from pickup import Subversion, Gitlab, Directory


class Test(unittest.TestCase):
    project = '/Volumes/Statics/Project/Company/mogujie'

    def test_svn_log(self):
        filename = self.project + '/appbeta/classes/controller/safe/admin.php'
        svn = Subversion.Subversion(filename)
        svn.log()
        self.assertEqual('foo'.upper(), 'FOO')

    def test_svn_diff(self):
        filename = self.project + '/appbeta/classes/controller/safe/admin.php'
        svn = Subversion.Subversion(filename, 'r717849', 'r718083')
        diff = svn.diff()
        # Print Result
        for event, values in diff.iteritems():
            print('{0} : {1}'.format(event, len(values)))

    def test_git(self):
        self.assertEqual('Test'.upper(), 'TEST')

    def test_directory(self):
        directory = Directory.Directory(self.project)
        directory.collect_files()


if __name__ == '__main__':
    unittest.main()
