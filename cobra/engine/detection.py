# -*- coding: utf-8 -*-

"""
    engine.detection
    ~~~~~~~~~~~~~~~~

    Implements framework detection

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
from cobra.utils.config import Config
from cobra.utils.log import logger
from pip.req import parse_requirements


class Detection(object):
    def __init__(self, target_directory, files):
        self.target_directory = target_directory
        self.directory = os.path.abspath(self.target_directory)
        self.files = files
        self.lang = None
        self.requirements = None

    @property
    def language(self):
        tmp_language = None
        for ext, ext_info in self.files:
            logger.info("{ext} {count}".format(ext=ext, count=ext_info['count']))
            rules = Config().rule()
            for language, language_info in rules['languages'].items():
                if ext in language_info['extensions']:
                    if 'chiefly' in language_info and language_info['chiefly'].lower() == 'true':
                        logger.debug('found the chiefly language({language}), maybe have largest, continue...'.format(language=language))
                        self.lang = language
                    else:
                        logger.debug('not chiefly, continue...'.format(language=language))
                        tmp_language = language
            if self.lang is None:
                logger.debug('not found chiefly language, use the largest language(language) replace'.format(language=tmp_language))
                self.lang = tmp_language
        logger.debug('main language({main_language}), tmp language({tmp_language})'.format(tmp_language=tmp_language, main_language=self.lang))
        return self.lang

    @property
    def framework(self):
        # initialize requirements data
        self._requirements()
        # TODO
        return 'Unknown Framework'
        frameworks = Config().rule()['languages'][self.lang]['frameworks']
        for framework in frameworks:
            # single framework
            logger.debug('{frame} - {code}'.format(frame=framework['name'], code=framework['code']))
            for method, rule in framework['rules'].items():
                rule = rule.strip().lower()
                # single rule
                if method == 'requirements':
                    logger.debug(' - requirements: {module}'.format(module=rule))
                    if rule in self.requirements:
                        return framework['name']
                elif method == 'file':
                    pass
                elif method == 'folder':
                    pass
        return 'Unknown Framework'

    def _requirements(self):
        requirements_txt = os.path.join(self.directory, 'requirements.txt')
        logger.debug(requirements_txt)
        if os.path.isfile(requirements_txt):
            requirements = parse_requirements(requirements_txt, session=False)
            self.requirements = [req.name.strip().lower() for req in requirements]
            logger.debug('requirements modules count: {count} ({modules})'.format(count=len(self.requirements), modules=','.join(self.requirements)))
        else:
            logger.debug('requirements.txt not found!')
            self.requirements = []
