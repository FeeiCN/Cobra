# -*- coding: utf-8 -*-

"""
    config
    ~~~~~~

    Implements config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import traceback
from .log import logger

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser

project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir))

code_path = '/tmp/cobra'
if os.path.isdir(code_path) is not True:
    os.mkdir(code_path)

running_path = os.path.join(code_path, 'running')
if os.path.isdir(running_path) is not True:
    os.mkdir(running_path)

package_path = os.path.join(code_path, 'package')
if os.path.isdir(package_path) is not True:
    os.mkdir(package_path)

source_path = os.path.join(code_path, 'git')
if os.path.isdir(source_path) is not True:
    os.mkdir(source_path)

issue_path = os.path.join(code_path, 'issue')
if os.path.isdir(issue_path) is not True:
    os.mkdir(issue_path)

export_path = os.path.join(code_path, 'export')
if not os.path.exists(export_path):
    os.mkdir(export_path)

issue_history_path = os.path.join(issue_path, 'history')
cobra_main = os.path.join(project_directory, 'cobra.py')
core_path = os.path.join(project_directory, 'cobra')
tests_path = os.path.join(project_directory, 'tests')
examples_path = os.path.join(tests_path, 'examples')
rules_path = os.path.join(project_directory, 'rules')
config_path = os.path.join(project_directory, 'config')
rule_path = os.path.join(project_directory, 'rule.cobra')


class Config(object):
    def __init__(self, level1=None, level2=None):
        self.level1 = level1
        self.level2 = level2
        if self.level1 is None and self.level2 is None:
            return
        self.config = ConfigParser()

        self.config.read(config_path)
        value = None
        try:
            value = self.config.get(self.level1, self.level2)
        except Exception as e:
            traceback.print_exc()
            logger.critical("./configs file configure failed. {u}\nError: {e}".format(u='http://cobra.feei.cn/config', e=e.message))
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

    def set(self, value):
        self.config.set(self.level1, self.level2, value)
        try:
            with open(config_path, 'w') as config_file:
                self.config.write(config_file)

        except IOError as e:
            traceback.print_exc()
            logger.warning('[CONFIG] ' + e.message)
            return False
        return True


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
