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


class Framework(object):
    def __init__(self, directory, language):
        self.directory = os.path.abspath(directory)
        self.language = language

        self.requirements = None

    def get_framework(self):
        if self.language is None:
            return 'Unknown'
        # initialize requirements data
        self._requirements()
        frameworks = Config().rule()['languages'][self.language]['frameworks']
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
