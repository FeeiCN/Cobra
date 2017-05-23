# -*- coding: utf-8 -*-

"""
    pickup.directory
    ~~~~~~~~~~~~~~~~

    Implements various directory

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
import os
from operator import itemgetter
from cobra.utils.log import logger


class Directory(object):
    def __init__(self, absolute_path):
        self.absolute_path = absolute_path

    file_sum = 0
    type_nums = {}
    result = {}
    file = []

    """
    :return {'.php': {'count': 2, 'list': ['/path/a.php', '/path/b.php']}}, file_sum, time_consume
    """

    def collect_files(self):
        t1 = time.clock()
        self.files(self.absolute_path)
        self.result['no_extension'] = {'count': 0, 'list': []}
        for extension, values in self.type_nums.items():
            extension = extension.strip()
            self.result[extension] = {'count': len(values), 'list': []}
            # .php : 123
            logger.debug('{0} : {1}'.format(extension, len(values)))
            for f in self.file:
                es = f.split(os.extsep)
                if len(es) >= 2:
                    # Exists Extension
                    # os.extsep + es[len(es) - 1]
                    if f.endswith(extension):
                        self.result[extension]['list'].append(f)
                else:
                    # Didn't have extension
                    self.result['no_extension']['count'] = int(self.result['no_extension']['count']) + 1
                    self.result['no_extension']['list'].append(f)
        if self.result['no_extension']['count'] == 0:
            del self.result['no_extension']
        t2 = time.clock()
        # reverse list count
        self.result = sorted(self.result.items(), key=itemgetter(1), reverse=False)
        return self.result, self.file_sum, t2 - t1

    def files(self, absolute_path, level=1):
        if level == 1:
            logger.debug(absolute_path)
        try:
            if os.path.isfile(absolute_path):
                filename, directory = os.path.split(absolute_path)
                self.file_info(directory, filename)
            else:
                for filename in os.listdir(absolute_path):
                    directory = os.path.join(absolute_path, filename)

                    # Directory Structure
                    logger.debug('|  ' * (level - 1) + '|--' + filename)
                    if os.path.isdir(directory):
                        self.files(directory, level + 1)
                    if os.path.isfile(directory):
                        self.file_info(directory, filename)
        except OSError as e:
            logger.critical('{msg}'.format(msg=e))
            exit()

    def file_info(self, path, filename):
        # Statistic File Type Count
        file_name, file_extension = os.path.splitext(path)
        self.type_nums.setdefault(file_extension.lower(), []).append(filename)

        path = path.replace(self.absolute_path, '')
        self.file.append(path)
        self.file_sum += 1
        logger.debug("{0}, {1}".format(self.file_sum, path))
