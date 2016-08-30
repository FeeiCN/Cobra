# -*- coding: utf-8 -*-

"""
    utils.config
    ~~~~~~~~~~~~

    Implements config

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
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
        try:
            value = config.get(level1, level2)
        except Exception as e:
            print("./config file configure failed.\nError: {0}\nSee Help: https://github.com/wufeifei/cobra/wiki/Config".format(e.message))
            exit()
        self.value = value
