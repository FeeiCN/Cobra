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


class File:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        f = open(self.file_path, 'r').readlines()
        return f
