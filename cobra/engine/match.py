# -*- coding: utf-8 -*-

"""
    engine.parse
    ~~~~~~~~~~~~

    Implements code syntax parse

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import re
import traceback
import subprocess
from cobra.engine.core import Core
from cobra.utils.log import logger
from cobra.utils import tool


class Match(object):
    def __init__(self, target_directory):
        self.directory = target_directory
        self.find = tool.find
        self.grep = tool.grep
        self.data = []

    def get(self, rule):
        if rule['match'] == "":
            mode = 'Find'
            filters = []
            for index, e in enumerate(rule['extensions']):
                if index > 1:
                    filters.append('-o')
                filters.append('-name')
                filters.append('*' + e)
            # Find Special Ext Files
            param = [self.find, self.directory, "-type", "f"] + filters
        else:
            mode = 'Grep'
            filters = []
            for e in rule['extensions']:
                filters.append('--include=*' + e)

            # explode dirs
            explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [self.grep, "-s", "-n", "-r", "-P"] + filters + [rule['match'], self.directory]
        logger.debug(' '.join(param))
        try:
            p = subprocess.Popen(param, stdout=subprocess.PIPE)
            result, error = p.communicate()
        except Exception as e:
            print(e)
            logger.critical('match exception ({e})'.format(e=e.message))
            return None
        if error is not None:
            logger.critical(error)
        # exists result
        if len(result):
            lines = str(result).strip().split("\n")
            logger.info('**Founded Vulnerability**\r\n > Vulnerability Count: `{count}`\r\n'.format(count=len(lines)))
            for index, line in enumerate(lines):
                line = line.strip()
                logger.info('Found: {line}'.format(line=line))
                if line == '':
                    continue
                # grep result
                if ':' in line:
                    #
                    # Rules
                    #
                    # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
                    # Projects/cobra/cobra/tests/examples/vulnerabilities.php:211:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
                    # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2134:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
                    # Projects/cobra/cobra/tests/examples/vulnerabilities.php:21111:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
                    # Projects/cobra/cobra/tests/examples/vulnerabilities.php:212344:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
                    try:
                        file_path, line_number, code_content = re.findall(r'(.*):(\d+):(.*)', line)[0]
                    except Exception as e:
                        logger.warning('match line parse exception')
                        continue
                else:
                    # search file
                    file_path = line
                    code_content = ''
                    line_number = 0
                # core rule check
                result_info = {
                    'project_id': None,
                    'project_directory': self.directory,
                    'rule_id': None,
                    'task_id': None,
                    'result_id': None,
                    'file_path': file_path,
                    'line_number': line_number,
                    'code_content': code_content,
                }
                logger.info(result_info)
                is_test = False
                try:
                    self.data += Core(result_info, rule, 'project name', ['whitelist1', 'whitelist2'], test=is_test, index=index).scan()
                except Exception as e:
                    traceback.print_exc()
            return self.data
        else:
            logger.info('Not Found')
            return None
