# -*- coding: utf-8 -*-

"""
    file
    ~~~~~~

    readfile by open/read for windows

    :author:    LoRexxar
    :homepage:  https://github.com/LoRexxar/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""

import re

ext_list = ['.php', '.php3', '.php4', '.php5', '.php7', '.pht', '.phs', '.phtml']


def file_list_parse(filelist):
    result = []

    if not filelist:
        return result

    for ext in ext_list:
        for file in filelist:
            if file[0] == ext:
                result.append(file[1]['list'])

    return result


def get_line(file_path, line_rule):
    """
    搜索指定文件的指定行到指定行的内容
    :param file_path: 指定文件
    :param line_rule: 指定行规则
    :return: 
    """
    s_line = int(line_rule.split(',')[0])
    e_line = int(line_rule.split(',')[1][:-1])
    result = []

    with open(file_path) as file:
        line_numer = 0
        for line in file:
            line_numer += 1
            if s_line <= line_numer <= e_line:
                result.append(line)

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
                        result.append(self.target + ffile + '||' + str(line_number) + '||' + line)

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

