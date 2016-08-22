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
import sys
import re
import subprocess
from utils import log


class Parse:
    def __init__(self, rule, file_path, line, code):
        self.rule = rule
        self.file_path = file_path
        self.line = line
        self.code = code

    def functions(self):
        # parse functions
        # `grep` (`ggrep` on Mac)
        grep = '/bin/grep'
        # `find` (`gfind` on Mac)
        find = '/bin/find'
        if 'darwin' == sys.platform:
            ggrep = ''
            for root, dir_names, file_names in os.walk('/usr/local/Cellar/grep'):
                for filename in file_names:
                    if 'ggrep' == filename or 'grep' == filename:
                        ggrep = os.path.join(root, filename)
            if ggrep == '':
                log.critical("brew install ggrep pleases!")
                sys.exit(0)
            else:
                grep = ggrep
        regex = r'(?:function\s+)(\w+)\s*'
        param = [grep, "-n", "-r", "-P"] + [regex, self.file_path]

        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = []
            print(result[0])
            index = 0
            lines = str(result[0]).split("\n")
            for line in lines:
                index += 1
                line = line.strip()
                if line == '':
                    continue
                function = line.split(':')
                if len(function) == 2:
                    function_name = re.findall(regex, function[1].strip())
                    if len(function_name) == 1:
                        function_name = function_name[0]
                        if index > 1:
                            functions[index - 2]['end'] = function[0]
                        if index == len(lines) - 1:
                            end = sum(1 for l in open(self.file_path))
                            log.info('File lines: {0}'.format(end))
                        else:
                            end = ''
                        functions.append({
                            'function': function_name,
                            'start': function[0],
                            'end': end  # next function's start
                        })
                    else:
                        log.info("Can't find function name: {0}".format(line))
            return functions
        else:
            return False

    def block_code(self, block_position):
        """
        Get block code
        :param block_position:
                0:up:1:down
        :return:
        """
        functions = self.functions()
        if functions:
            block_start = 0
            block_end = 0
            for function in functions:
                # log.debug('{0} < {1} < {2}'.format(function['start'], self.line, function['end']))
                if int(function['start']) < int(self.line) < int(function['end']):
                    if block_position == 0:
                        block_start = function['start']
                        block_end = int(self.line) - 1
                    elif block_position == 1:
                        block_start = int(self.line) + 1
                        block_end = function['end']
            # get param block code
            param = ['sed', "-n", "{0},{1}p".format(block_start, block_end), self.file_path]
            p = subprocess.Popen(param, stdout=subprocess.PIPE)
            result = p.communicate()
            if len(result[0]):
                param_block_code = result[0]
            else:
                param_block_code = ''
            return param_block_code
        else:
            log.info("Not found functions")
            return False

    def is_controllable_param(self):
        param_name = re.findall(self.rule, self.code)
        if len(param_name) == 1:
            print(param_name)
            param_name = param_name[0].strip()
            log.info('Param name: {0}'.format(param_name))
            # controllable param
            if param_name[:1] == '$':
                # get param block code
                param_block_code = self.block_code(0)
                # check = "" or = ''
                """
                check string
                $param_name = ""
                $param_name = ''
                """
                log.info("Check un controllable param ```{0}``` =".format(param_name))
                un_controllable_param_rule = [
                    # ```$param_name = 'http://wufeifei.com'```
                    r'\{0}\s?=\s?\'((\?(?=\\\\\')..|[^\'])*)\''.format(param_name),
                    # ```$param_name = "http://wufeifei.com"```
                    r'\{0}\s?=\s?"((\?(?=\\\\")..|[^"])*)"'.format(param_name)
                ]
                for uc_rule in un_controllable_param_rule:
                    uc_rule_result = re.findall(uc_rule, param_block_code)
                    if len(uc_rule_result) >= 1:
                        log.info("```$param_name = ''``` : {0} = {1}".format(param_name, uc_rule_result[0]))
                        return False

                log.info("Check controllable param rule")
                controllable_param_rule = [
                    {
                        'rule': r'\\s?=\s?(\$\w+(?:\[(?:[^[\]]|(\?R))*\])*)'.format(param_name),
                        'example': '$param_name = $variable',
                        'test': """
                            $param_name = $_GET
                            $param_name = $_POST
                            $param_name = $_REQUEST
                            $param_name = $_COOKIE
                            $param_name = $var
                            """
                    },
                    {
                        'rule': r'function\s+\w+\s?\(.*(\{0})'.format(param_name),
                        'example': 'function ($param_name)',
                        'test': """
                            function ($param_name)
                            function ($some, $param_name)
                            """
                    }

                ]
                for c_rule in controllable_param_rule:
                    c_rule_result = re.findall(c_rule['rule'], param_block_code)
                    if len(c_rule_result) >= 1:
                        log.info("New rule: controllable param: {0}, {1}".format(param_name, c_rule['example']))
                        return True
                return True
            else:
                return False

    def is_repair(self, repair_rule, block_repair):
        code = self.block_code(block_repair)
        repair_result = re.findall(repair_rule, code)
        if len(repair_result) >= 1:
            log.info("Repaired")
            return True
        else:
            log.info("Un Repair")
            return False


if __name__ == '__main__':
    parse = Parse('curl_setopt\s?\(.*,\s?CURLOPT_URL\s?,(.*)\)', '/tmp/cobra/versions/mogujie/appbeta/classes/admin/book.php', '3222', 'curl_setopt($ch,CURLOPT_URL,$url);')
    if parse.is_controllable_param():
        parse.is_repair(r'curl_setopt\s?\(.*,\s?CURLOPT_PROTOCOLS\s?,(.*)\)', 1)
