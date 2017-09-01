# -*- coding: utf-8 -*-

"""
    pickup
    ~~~~~~

    readfile by open/read for windows

    :author:    LoRexxar
    :homepage:  https://github.com/LoRexxar/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""

from .pickup import Directory
import os
import re

ext_list = ['.php', '.php3', '.php4', '.php5', '.php7', '.pht', '.phs', '.phtml']


def file_list_parse(filelist):
    result = []
    for ext in ext_list:
        for file in filelist:
            if file[0] == ext:
                result.append(file[1]['list'])

    return result


class File:
    def __init__(self, filelist, target):
        self.filelist = filelist
        self.t_filelist = file_list_parse(filelist)[0]
        self.target = target

    def grep(self, reg):
        """
        遍历目标filelist，匹配文件内容
        :param reg: 内容匹配正则
        :return: 
        """
        result = []

        for ffile in self.t_filelist:
            with open(self.target+ffile) as file:
                line_number = 0
                for line in file:
                    line_number += 1
                    # print line, line_number
                    if re.search(reg, line, re.I):
                        result.append(self.target + ffile + ':' + str(line_number) + ':' + line)

        return result

    def find(self, ext):
        """
        搜索指定后缀的文件
        :param ext: 后缀名
        :return: 
        """
        for file in self.filelist:
            if file[0] == ext:
                return file[1]['list']

target_directory = os.path.abspath('./tests/vulnerabilities')
files, file_count, time_consume = Directory(target_directory).collect_files()

f = File(files, target_directory)

# print f.grep("(\"\s*(select|SELECT|insert|INSERT|update|UPDATE)\s*(([^;]\s*)*)?\$(.+?);?\")")
print f.find(".m")
