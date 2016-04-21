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
from pickup import subversion


class Test(unittest.TestCase):
    def test_svn_log(self):
        project = '/Volumes/Statics/Project/Company/mogujie'
        file = project + '/appbeta/classes/controller/safe/admin.php'
        subversion.log(file)
        self.assertEqual('foo'.upper(), 'FOO')

    def test_svn_diff(self):
        project = '/Volumes/Statics/Project/Company/mogujie'
        file = project + '/appbeta/classes/controller/safe/admin.php'
        diff = subversion.diff(file, 'r717849', 'r718083')

    def test_git(self):
        self.assertEqual('Test'.upper(), 'TEST')


if __name__ == '__main__':
    unittest.main()
