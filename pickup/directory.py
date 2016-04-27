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
import time
import os


class Directory:
    def __init__(self, path):
        self.path = path

    file_nums = 0
    type_nums = {}

    def files(self, directory, level=1):
        if level == 1:
            print directory
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)

            # Statistic File Type Numbers
            file_name, file_extension = os.path.splitext(path)
            self.type_nums.setdefault(file_extension.lower(), []).append(filename)

            # Directory Structure
            print '|  ' * (level - 1) + '|--' + filename
            if os.path.isdir(path):
                self.files(path, level + 1)
            if os.path.isfile(path):
                self.file_nums += 1

    def collect_files(self):
        result = {}
        t1 = time.clock()
        self.files(self.path)
        t2 = time.clock()
        print('Scan Files: {0}, Total Time: {1}s'.format(self.file_nums, t2 - t1))
        for extension, values in self.type_nums.iteritems():
            print('{0} : {1}'.format(extension, len(values)))