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
import os
import ConfigParser


class Config:
    def __init__(self, level1=None, level2=None):
        self.project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        if level1 is None and level2 is None:
            return
        config = ConfigParser.ConfigParser()

        config_file = os.path.join(self.project_directory, 'config')
        config.read(config_file)
        self.value = config.get(level1, level2)
