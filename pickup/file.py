# -*- coding: utf-8 -*-

"""
    pickup.file
    ~~~~~~~~~~~

    Implements various file

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import subprocess


class File:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        """
        读取文件内容
        :return:
        """
        f = open(self.file_path, 'r').readlines()
        return f

    def lines(self, line_rule):
        """
        获取指定行内容
        :param line_rule:
        :return:
        """
        param = ['sed', "-n", line_rule, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            content = result[0]
            if content == '':
                content = False
        else:
            content = False
        return content
