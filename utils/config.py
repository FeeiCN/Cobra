# -*- coding: utf-8 -*-

"""
    utils.config
    ~~~~~~~~~~~~

    Implements config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import StringIO
import ConfigParser


class Config(object):
    def __init__(self, level1=None, level2=None):
        self.level1 = level1
        self.level2 = level2
        self.project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
        if level1 is None and level2 is None:
            return
        config = ConfigParser.ConfigParser()

        config_file = os.path.join(self.project_directory, 'config')
        config.read(config_file)
        value = None
        try:
            value = config.get(level1, level2)
        except Exception as e:
            print("./config file configure failed.\nError: {0}\nSee Help: http://cobra-docs.readthedocs.io/en/latest/configuration/".format(e.message))
            exit()
        self.value = value


def properties(config_path):
    if os.path.isfile(config_path) is not True:
        return dict()
    with open(config_path) as f:
        config = StringIO.StringIO()
        config.write('[dummy_section]\n')
        config.write(f.read().replace('%', '%%'))
        config.seek(0, os.SEEK_SET)

        cp = ConfigParser.SafeConfigParser()
        cp.readfp(config)

        return dict(cp.items('dummy_section'))
