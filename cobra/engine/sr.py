# -*- coding: utf-8 -*-

"""
    engine.parse
    ~~~~~~~~~~~~

    Implements Single Rule Process

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import re
import traceback
import subprocess
from cobra.engine.core import Core
from cobra.engine.result import VulnerabilityResult
from cobra.utils.log import logger
from cobra.utils import tool


class SingleRule(object):
    def __init__(self, target_directory, single_rule):
        self.directory = target_directory
        self.find = tool.find
        self.grep = tool.grep
        self.sr = single_rule
        # Single Rule Vulnerabilities
        """
        [
            vr
        ]
        """
        self.srv = []

    def process(self):
        """
        Process Single Rule
        :return: SRV(Single Rule Vulnerabilities)
        """
        results = self.match_results()
        # exists result
        if results == '':
            logger.info('Not found any match...')
            return None

        matches = str(results).strip().split("\n")
        logger.info('**Founded Vulnerability**\r\n > Vulnerability Count: `{count}`\r\n'.format(count=len(matches)))
        for index, single_match in enumerate(matches):
            single_match = single_match.strip()
            logger.debug('Found: {line}'.format(line=single_match))
            if single_match == '':
                continue
            vr = self.parse_match(single_match)
            is_test = False
            try:
                is_vulnerability, code = Core(self.directory, vr, self.sr, 'project name', ['whitelist1', 'whitelist2'], test=is_test, index=index).scan()
                if is_vulnerability:
                    logger.info('Found {code}'.format(code=code))
                    self.srv.append(vr)
                else:
                    logger.info('Not vulnerability: {code}'.format(code=code))
            except Exception as e:
                traceback.print_exc()
        return self.srv

    def match_results(self):
        if self.sr['match'] == "":
            mode = 'Find'
            filters = []
            for index, e in enumerate(self.sr['extensions']):
                if index > 1:
                    filters.append('-o')
                filters.append('-name')
                filters.append('*' + e)
            # Find Special Ext Files
            param = [self.find, self.directory, "-type", "f"] + filters
        else:
            mode = 'Grep'
            filters = []
            for e in self.sr['extensions']:
                filters.append('--include=*' + e)

            # explode dirs
            explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [self.grep, "-s", "-n", "-r", "-P"] + filters + [self.sr['match'], self.directory]
        logger.debug(' '.join(param))
        try:
            p = subprocess.Popen(param, stdout=subprocess.PIPE)
            result, error = p.communicate()
        except Exception as e:
            traceback.print_exc()
            logger.critical('match exception ({e})'.format(e=e.message))
            return None
        if error is not None:
            logger.critical(error)
        return result

    def parse_match(self, single_match):
        mr = VulnerabilityResult()
        # grep result
        if ':' in single_match:
            #
            # Rules
            #
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:211:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2134:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:21111:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:212344:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            try:
                mr.file_path, mr.line_number, mr.code_content = re.findall(r'(.*):(\d+):(.*)', single_match)[0]
            except Exception as e:
                logger.warning('match line parse exception')
                mr.file_path = ''
                mr.code_content = ''
                mr.line_number = 0
        else:
            # search file
            mr.file_path = single_match
            mr.code_content = ''
            mr.line_number = 0
        return mr
