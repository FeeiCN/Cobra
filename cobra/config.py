# -*- coding: utf-8 -*-

"""
    config
    ~~~~~~

    Implements config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import StringIO
import ConfigParser
import traceback
from .log import logger

project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))
code_path = '/tmp'
core_path = os.path.join(project_directory, 'cobra')
tests_path = os.path.join(project_directory, 'tests')
examples_path = os.path.join(tests_path, 'examples')
rules_path = os.path.join(project_directory, 'rules')
config_path = os.path.join(project_directory, 'config.cobra')
rule_path = os.path.join(project_directory, 'rule.cobra')


class Config(object):
    def __init__(self, level1=None, level2=None):
        self.level1 = level1
        self.level2 = level2
        if level1 is None and level2 is None:
            return
        config = ConfigParser.ConfigParser()

        config.read(config_path)
        value = None
        try:
            value = config.get(level1, level2)
        except Exception as e:
            print(level1, level2)
            traceback.print_exc()
            print("./configs file configure failed.\nError: {0}\nSee Help: http://cobra-docs.readthedocs.io/en/latest/configuration/".format(e.message))
        self.value = value

    @staticmethod
    def copy(source, destination):
        if os.path.isfile(destination) is not True:
            logger.info('Not set configuration, setting....')
            with open(source) as f:
                content = f.readlines()
            with open(destination, 'w+') as f:
                f.writelines(content)
            logger.info('Config file set success(~/.cobra/{source})'.format(source=source))
        else:
            return


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


class Vulnerabilities(object):
    def __init__(self, key):
        self.key = key

    def status_description(self):
        status = {
            0: 'Not fixed',
            1: 'Not fixed(Push third-party)',
            2: 'Fixed'
        }
        if self.key in status:
            return status[self.key]
        else:
            return False

    def repair_description(self):
        repair = {
            0: 'Initialize',
            1: 'Fixed',
            4000: 'File not exist',
            4001: 'Special file',
            4002: 'Whitelist',
            4003: 'Test file',
            4004: 'Annotation',
            4005: 'Modify code',
            4006: 'Empty code',
            4007: 'Const file',
            4008: 'Third-party'
        }
        if self.key in repair:
            return repair[self.key]
        else:
            return False

    def level_description(self):
        level = {
            0: 'Undefined',
            1: 'Low',
            2: 'Medium',
            3: 'High',
        }
        if self.key in level:
            return level[self.key]
        else:
            return False
