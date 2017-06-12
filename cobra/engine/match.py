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
import subprocess
from cobra.pickup.file import File
from cobra.utils.config import Config
from cobra.utils.log import logger
from cobra.utils import tool


class Match(object):
    def __init__(self):
        rules = Config().rule()
        for vn, vi in rules['vulnerabilities'].items():
            # single vulnerability
            logger.info('{vn} ({vn_description})'.format(vn=vn, vn_description=vi['name']))
            for rule in vi['rules']:
                # single vulnerability rule
                logger.info(" > {vn}".format(vn=rule['name']))
                logger.debug(""" 
                    Language: {language}
                    Match: {match}
                    Repair: {repair}""".format(
                    language=rule['language'],
                    match=rule['match'],
                    repair=rule['repair']
                ))

                # execute match

    def get(self):
        if rule['match'] == "":
            mode = 'Find'
            filters = []
            for index, e in enumerate(extensions):
                if index > 1:
                    filters.append('-o')
                filters.append('-name')
                filters.append('*' + e)
            # Find Special Ext Files
            param = [find, self.directory, "-type", "f"] + filters
        else:
            mode = 'Grep'
            filters = []
            for e in extensions:
                filters.append('--include=*' + e)

            # explode dirs
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [grep, "-s", "-n", "-r", "-P"] + filters + [rule['match'], self.directory]
        logger.info('**Rule Info({index})**\r\n > ID: `{rid}` \r\n > Name: `{name}` \r\n > Language: `{language}`\r\n > Rule mode:`{mode}`\r\n > Location: `{location}` \r\n > Repair: `{repair} `\r\n'.format(index=index, rid=rule.id, name=rule.description, language=extensions, mode=mode, location=rule['match'], repair=rule.regex_repair))
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()

        # exists result
        if len(result[0]):
            lines = str(result[0]).strip().split("\n")
            logger.info('**Founded Vulnerability**\r\n > Vulnerability Count: `{count}`\r\n'.format(count=len(lines)))
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    continue
                # grep result
                if ':' in line:
                    line_split = line.split(':', 1)
                    file_path = line_split[0].strip()
                    code_content = line_split[1].split(':', 1)[1].strip()
                    line_number = line_split[1].split(':', 1)[0].strip()
                else:
                    # search file
                    file_path = line
                    code_content = ''
                    line_number = 0
                # core rule check
                result_info = {
                    'task_id': self.task_id,
                    'project_id': self.project_id,
                    'project_directory': self.directory,
                    'rule_id': rule.id,
                    'result_id': None,
                    'file_path': file_path,
                    'line_number': line_number,
                    'code_content': code_content,
                    'third_party_vulnerabilities_name': vulnerability_types[rule.vul_id]['name'],
                    'third_party_vulnerabilities_type': vulnerability_types[rule.vul_id]['third_v_id']
                }
                self.data += Core(result_info, rule, self.project_name, white_list, test=test, index=index).scan()
        else:
            logger.info('Not Found')
