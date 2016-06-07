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
import os


class Directory:
    def __init__(self, path):
        self.path = path

    file_nums = 0
    type_nums = {}
    result = {}
    file = []

    def files(self, directory, level=1):
        if level == 1:
            print directory
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)

            # Statistic File Type Count
            file_name, file_extension = os.path.splitext(path)
            self.type_nums.setdefault(file_extension.lower(), []).append(filename)

            # Directory Structure
            # print '|  ' * (level - 1) + '|--' + filename
            if os.path.isdir(path):
                self.files(path, level + 1)
            if os.path.isfile(path):
                path = path.replace(self.path, '')
                self.file.append(path)
                self.file_nums += 1
                print("{0}, {1}".format(self.file_nums, path))

    def collect_files(self):
        t1 = time.clock()
        self.files(self.path)
        for extension, values in self.type_nums.iteritems():
            self.result[extension] = {'file_count': len(values), 'file_list': []}
            print('{0} : {1}'.format(extension, len(values)))
            for f in self.file:
                if f.endswith(extension):
                    self.result[extension]['file_list'].append(f)

        t2 = time.clock()
        print('Scan Files: {0}, Total Time: {1}s'.format(self.file_nums, t2 - t1))
        self.result['file_nums'] = self.file_nums
        return self.result
