# -*- coding: utf-8 -*-

"""
    pickup.directory
    ~~~~~~~~~~~~~~~~

    Implements various directory

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time
import os
from utils import log
from app import db, CobraExt


class Directory:
    def __init__(self, path):
        self.path = path

    file_id = 0
    type_nums = {}
    result = {}
    file = []

    def files(self, directory, level=1):
        if level == 1:
            log.debug(directory)
        for filename in os.listdir(directory):
            path = os.path.join(directory, filename)

            # Statistic File Type Count
            file_name, file_extension = os.path.splitext(path)
            self.type_nums.setdefault(file_extension.lower(), []).append(filename)

            # Directory Structure
            # log.debug('|  ' * (level - 1) + '|--' + filename)
            if os.path.isdir(path):
                self.files(path, level + 1)
            if os.path.isfile(path):
                path = path.replace(self.path, '')
                self.file.append(path)
                self.file_id += 1
                log.debug("{0}, {1}".format(self.file_id, path))

    """
    :return {'file_nums': 50, 'collect_time': 2, '.php': {'file_count': 2, 'file_list': ['/path/a.php', '/path/b.php']}}
    """

    def collect_files(self, task_id=None):
        t1 = time.clock()
        self.files(self.path)
        self.result['no_extension'] = {'file_count': 0, 'file_list': []}
        for extension, values in self.type_nums.items():
            extension = extension.strip()
            self.result[extension] = {'file_count': len(values), 'file_list': []}
            # .php : 123
            log.debug('{0} : {1}'.format(extension, len(values)))
            if task_id is not None:
                # Store
                ext = CobraExt(task_id, extension, len(values))
                db.session.add(ext)
            for f in self.file:
                es = f.split(os.extsep)
                if len(es) >= 2:
                    # Exists Extension
                    # os.extsep + es[len(es) - 1]
                    if f.endswith(extension):
                        self.result[extension]['file_list'].append(f)
                else:
                    # Didn't have extension
                    self.result['no_extension']['file_count'] = int(self.result['no_extension']['file_count']) + 1
                    self.result['no_extension']['file_list'].append(f)
        if task_id is not None:
            db.session.commit()
        t2 = time.clock()
        self.result['file_nums'] = self.file_id
        self.result['collect_time'] = t2 - t1
        return self.result
