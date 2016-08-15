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
from utils import log


class Detection:
    def __init__(self, project_directory=None):
        self.project_directory = project_directory
        self.rules = [
            {
                'name': 'Kohana',
                'site': 'http://kohanaframework.org/',
                'source': 'https://github.com/kohana/kohana',
                'rules': {
                    'directory': 'system/guide/kohana',
                    'file': 'system/config/userguide.php',
                },
                'public': 'public'
            },
            {
                'name': 'Laravel',
                'site': 'http://laravel.com/',
                'source': 'https://github.com/laravel/laravel',
                'rules': {
                    'file': 'artisan'
                }
            },
            {
                'name': 'ThinkPHP',
                'site': 'http://www.thinkphp.cn/',
                'source': 'https://github.com/top-think/thinkphp',
                'rules': {
                    'file': 'ThinkPHP/ThinkPHP.php'
                }
            },
            {
                'name': 'CodeIgniter',
                'site': 'https://codeigniter.com/',
                'source': 'https://github.com/bcit-ci/CodeIgniter',
                'rules': {
                    'file': 'system/core/CodeIgniter.php'
                }
            }
        ]

    def framework(self):
        """
        Detection framework for project
        :return:
        """
        for rule in self.rules:
            log.info("Name: {0} Site: {1} Source: {2}".format(rule['name'], rule['site'], rule['source']))
            rules_types = ['file', 'directory']
            rules_count = len(rule['rules'])
            rules_completed = 0
            log.info('Rules Count: {0} Rules Info: {1}'.format(rules_count, rule['rules']))
            for rule_type in rules_types:
                if rule_type in rule['rules']:
                    target = os.path.join(self.project_directory, rule['rules'][rule_type])
                    log.debug('Detection({0}): {1}'.format(rule_type, target))
                    if rule_type == 'file':
                        if os.path.isfile(target):
                            rules_completed += 1
                    elif rule_type == 'directory':
                        if os.path.isdir(target):
                            rules_completed += 1
            if rules_completed == rules_count:
                log.info("Framework: {0}".format(rule['name']))
                return rule['name']
        return None


if __name__ == '__main__':
    Detection('/tmp/cobra/versions/mogujie/').framework()
