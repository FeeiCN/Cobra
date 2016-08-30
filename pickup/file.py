#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Feei. All Rights Reserved
#
# :author:   Feei <wufeifei@wufeifei.com>
# :homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'docs/COPYING' for copying permission
#


class File:
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        f = open(self.file_path, 'r').readlines()
        return f
