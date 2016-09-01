#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    engine.parse
    ~~~~~~~~~~~~

    Implements code syntax parse

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import sys
import re
import subprocess
import traceback
from utils import log


class Parse:
    """
    Parse code syntax
    """

    def __init__(self, rule, file_path, line, code):
        self.rule = rule
        self.file_path = file_path
        log.info(file_path)
        self.line = line
        self.code = code

    def functions(self):
        # parse functions
        # `grep` (`ggrep` on Mac)
        grep = '/bin/grep'
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
        regex = r'(?:function\s+)(\w+)\s*\('
        param = [grep, "-n", "-r", "-P"] + [regex, self.file_path]

        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = {}
            # log.debug(result[0])
            lines = str(result[0]).strip().split("\n")
            prev_function_name = ''
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    log.info('Empty')
                    continue
                function = line.split(':')
                if len(function) >= 2 and function[1].strip()[:2] not in ['//', '#', '/*']:
                    function_name = re.findall(regex, function[1].strip())
                    if len(function_name) == 1:
                        function_name = function_name[0]
                        log.info('Function name: {0} - {1} - Prev Func: {2}'.format(index, function_name, prev_function_name))
                        if index > 0:
                            functions[prev_function_name]['end'] = function[0]
                        if index == len(lines) - 1:
                            end = sum(1 for l in open(self.file_path))
                            log.info('File lines: {0}'.format(end))
                        else:
                            end = None
                        prev_function_name = function_name
                        functions[function_name] = {
                            'function': function_name,
                            'start': function[0],
                            'end': end  # next function's start
                        }
                    else:
                        log.info("Can't find function name: {0}".format(line))
                else:
                    print("没有分隔符(:)或改行为注释 {0}".format(function[1]))
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
            for function_name, function_value in functions.items():
                log.info("Function S-E: {0} ({1} - {2})".format(function_name, function_value['start'], function_value['end']))
                # log.debug('{0} < {1} < {2}'.format(function['start'], self.line, function['end']))
                if int(function_value['start']) < int(self.line) < int(function_value['end']):
                    if block_position == 0:
                        block_start = function_value['start']
                        block_end = int(self.line) - 1
                    elif block_position == 1:
                        block_start = int(self.line) + 1
                        block_end = function_value['end']
            # get param block code
            param = ['sed', "-n", "{0},{1}p".format(block_start, block_end), self.file_path]
            p = subprocess.Popen(param, stdout=subprocess.PIPE)
            result = p.communicate()
            if len(result[0]):
                param_block_code = result[0]
                if param_block_code == '':
                    param_block_code = False
            else:
                param_block_code = False
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
            # exclude class const (maybe misuse)
            class_const = re.findall(r'\$this->([_A-Z]*)', param_name)
            if len(class_const) >= 1 and class_const[0] != '':
                log.info("Return: $param_name = class const")
                return False
            if param_name[:1] == '$':
                # get param block code
                param_block_code = self.block_code(0)
                if param_block_code is False:
                    log.info("Found: param block code cant match")
                    return True
                log.debug(param_block_code)
                # check = "" or = ''
                """
                check string
                $param_name = ""
                $param_name = ''
                """
                log.info("Check un controllable param ```{0}``` = 'something'".format(param_name))
                un_controllable_param_rule = [
                    # ```$param_name = 'http://wufeifei.com'```
                    r'\{0}\s?=\s?\'((\?(?=\\\\\')..|[^\'])*)\''.format(param_name),
                    # ```$param_name = "http://wufeifei.com"```
                    r'\{0}\s?=\s?"((\?(?=\\\\")..|[^"])*)"'.format(param_name),
                    # ```$param_name = CONST_VARIABLE```
                    r'\$path\s?=\s?([A-Z_]*)'.format(param_name)
                ]
                for uc_rule in un_controllable_param_rule:
                    uc_rule_result = re.findall(uc_rule, param_block_code)
                    if len(uc_rule_result) >= 1:
                        log.info("Found: ```$param_name = ''``` : {0} = {1}".format(param_name, uc_rule_result[0]))
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
                log.info("Not contained $")
                return False

    def is_repair(self, repair_rule, block_repair):
        code = self.block_code(block_repair)
        if code is False:
            log.info("Return: repair code not match")
            return False
        repair_result = re.findall(repair_rule, code)
        log.debug(code)
        log.debug(repair_result)
        if len(repair_result) >= 1:
            log.info("Repaired")
            return True
        else:
            log.info("Un Repair")
            return False


if __name__ == '__main__':
    try:
        parse = Parse('unserialize\s*\(\s*(.+?)\s*\)', '/tmp/cobra/versions/mogujie/appbeta/classes/controller/zadmin/mobile/appbackend/resource.php', '92', "$info      = unserialize($item_info['info']);")
        if parse.is_controllable_param():
            parse.is_repair(r'fff', 0)
    except Exception as e:
        print(traceback.print_exc())
