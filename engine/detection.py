#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    engine.detection
    ~~~~~~~~~~~~~~~~

    Implements framework detection

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
from utils import log


class Detection:
    def __init__(self, project_directory=None):
        self.project_directory = project_directory
        self.rules = [
            {
                'name': 'Kohana',
                'language': 'PHP',
                'site': 'http://kohanaframework.org/',
                'source': 'https://github.com/kohana/kohana',
                'rules': {
                    'directory': 'system/guide/kohana',
                    'file': 'system/config/userguide.php',
                },
                'public': '/public'
            },
            {
                'name': 'Laravel',
                'language': 'PHP',
                'site': 'http://laravel.com/',
                'source': 'https://github.com/laravel/laravel',
                'rules': {
                    'file': '/artisan'
                }
            },
            {
                'name': 'ThinkPHP',
                'language': 'PHP',
                'site': 'http://www.thinkphp.cn/',
                'source': 'https://github.com/top-think/thinkphp',
                'rules': {
                    'file': '/ThinkPHP/ThinkPHP.php'
                }
            },
            {
                'name': 'CodeIgniter',
                'language': 'PHP',
                'site': 'https://codeigniter.com/',
                'source': 'https://github.com/bcit-ci/CodeIgniter',
                'rules': {
                    'file': '/system/core/CodeIgniter.php'
                }
            },
            {
                'name': 'Tesla/MWP',
                'language': 'Java',
                'site': 'http://www.mogujie.com/',
                'source': 'http://www.mogujie.com/',
                'rules': {
                    'file': '/pom.xml'
                }
            },
            {
                'name': 'Drupal',
                'language': 'PHP',
                'site': 'https://drupal.org/project/drupal',
                'source': 'https://github.com/drupal/drupal',
                'rules': {
                    'file': '/core/misc/drupal.js'
                }
            },
            {
                'name': 'Joomla',
                'language': 'PHP',
                'site': 'https://www.joomla.org/',
                'source': 'https://github.com/joomla/joomla-cms',
                'rules': {
                    'file': '/media/system/js/validate.js'
                }
            },
            {
                'name': 'Wordpress',
                'language': 'PHP',
                'site': 'http://wordpress.org/',
                'source': 'https://github.com/WordPress/WordPress',
                'rules': {
                    'file': '/wp-admin/wp-admin.css',
                    'file2': 'wp-includes/js/tinymce/tiny_mce_popup.js'
                }
            },
        ]

    def framework(self):
        """
        Detection framework for project
        :param: framework | language
        :return: self.rules['name']
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
                return rule['name'], rule['language']
        return '', ''


if __name__ == '__main__':
    Detection('/tmp/cobra/versions/mogujie').framework()
