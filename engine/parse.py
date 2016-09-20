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
import logging

log.Log()
logging = logging.getLogger(__name__)


class Parse:
    """
    Parse code syntax
    """

    def __init__(self, rule, file_path, line, code):
        logging.info('--------- [1]. Parse code syntax ---------')
        self.rule = rule
        self.file_path = file_path
        logging.info(file_path)
        self.line = line
        self.code = code
        self.param_name = None
        self.param_value = None

    def functions(self):
        logging.info('--------- [-]. Functions ---------')
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
                logging.critical("brew install ggrep pleases!")
                sys.exit(0)
            else:
                grep = ggrep
        regex = r'(?:function\s+)(\w+)\s*\('
        param = [grep, "-n", "-r", "-P"] + [regex, self.file_path]

        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = {}
            # logging.debug(result[0])
            lines = str(result[0]).strip().split("\n")
            prev_function_name = ''
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    logging.info('Empty')
                    continue
                function = line.split(':')
                if len(function) >= 2 and function[1].strip()[:2] not in ['//', '#', '/*']:
                    function_name = re.findall(regex, function[1].strip())
                    if len(function_name) == 1:
                        function_name = function_name[0]
                        logging.debug('F: {0}.{1} - PF: {2}'.format(index, function_name, prev_function_name))
                        if index > 0 and prev_function_name in functions:
                            functions[prev_function_name]['end'] = function[0]
                        prev_function_name = function_name
                        functions[function_name] = {
                            'start': function[0],
                            'end': None  # next function's start
                        }
                    else:
                        logging.info("Can't find function name: {0}".format(line))
                else:
                    logging.info("can't found (:) or this line is comment {0}".format(function[1]))
            end = sum(1 for l in open(self.file_path))
            for name, value in functions.items():
                if value['end'] is None:
                    functions[name]['end'] = end
            return functions
        else:
            return False

    def block_code(self, block_position):
        """
        获取区块代码
        :param block_position:
                0:up 上
                1:down 下
                2:location_line 当前行
        :return:
        """
        logging.info('--------- [-]. Block code B:{0} ---------'.format(block_position))
        if block_position == 2:
            if self.line is None or self.line == 0:
                logging.critical("Line number exception: {0}".format(self.line))
                return False
            line_rule = '{0}p'.format(self.line)
            code = self.get_code(line_rule)
            code = code.strip()
            logging.info("C: {0}".format(code))
            return code
        else:
            block_start = 0
            block_end = 0
            functions = self.functions()
            if functions:
                for function_name, function_value in functions.items():
                    in_this_function = ''
                    if int(function_value['start']) < int(self.line) < int(function_value['end']):
                        in_this_function = '<---- {0}'.format(self.line)
                        if block_position == 0:
                            block_start = function_value['start']
                            block_end = int(self.line) - 1
                        elif block_position == 1:
                            block_start = int(self.line) + 1
                            block_end = function_value['end']
                    logging.debug("F: {0} ({1} - {2}) {3}".format(function_name, function_value['start'], function_value['end'], in_this_function))
            else:
                # 没有functions时,以触发行来分割整个文件
                if block_position == 0:
                    block_start = 0
                    block_end = int(self.line) - 1
                elif block_position == 1:
                    block_start = int(self.line) + 1
                    block_end = sum(1 for l in open(self.file_path))
                logging.debug("Not found functions, split file.")
            # get param block code
            logging.info('B: {0} - {1}p'.format(block_start, block_end))
            line_rule = "{0},{1}p".format(block_start, block_end)
            return self.get_code(line_rule)

    def get_code(self, line_rule):
        param = ['sed', "-n", line_rule, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            param_block_code = result[0]
            if param_block_code == '':
                param_block_code = False
        else:
            param_block_code = False
        return param_block_code

    def is_controllable_param(self):
        logging.info('--------- [2]. Param is controllable ---------')
        param_name = re.findall(self.rule, self.code)
        if len(param_name) == 1:
            param_name = param_name[0].strip()
            self.param_name = param_name
            logging.info('P: {0}'.format(param_name))
            # controllable param
            # exclude class const (maybe misuse)
            class_const = re.findall(r'\$this->([_A-Z]*)', param_name)
            if len(class_const) >= 1 and class_const[0] != '':
                logging.info("R: False ($param = CONST || $this->CONST)")
                return False
            if param_name[:1] == '$':
                # get param block code
                param_block_code = self.block_code(0)
                if param_block_code is False:
                    logging.info("R: True (param block code can't match)")
                    return True
                logging.debug(param_block_code)
                # check = "" or = ''
                """
                check string
                $param_name = ""
                $param_name = ''
                """
                logging.info("Check un controllable param {0} = 'something'".format(param_name))
                un_controllable_param_rule = [
                    # ```$param_name = 'http://wufeifei.com'```
                    r'\{0}\s?=\s?\'((\?(?=\\\\\')..|[^\'])*)\''.format(param_name),
                    # ```$param_name = "http://wufeifei.com"```
                    r'\{0}\s?=\s?"((\?(?=\\\\")..|[^"])*)"'.format(param_name),
                    # ```$param_name = CONST_VARIABLE```
                    r'\$path\s?=\s?([A-Z_]*)'.format(param_name)
                ]
                for uc_rule in un_controllable_param_rule:
                    uc_rule_result = re.findall(re.escape(uc_rule), param_block_code)
                    if len(uc_rule_result) >= 1:
                        logging.info("R: False ($param = '' : {0} = {1})".format(param_name, uc_rule_result[0]))
                        return False

                logging.info("Check controllable param rule")
                controllable_param_rule = [
                    {
                        'rule': r'(\{0}\s?=\s?\$\w+(?:\[(?:[^[\]]|\?R)*\])*)'.format(param_name),
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
                        'rule': r'(function\s*\w+\s*\(.*\{0})'.format(param_name),
                        'example': 'function ($param_name)',
                        'test': """
                            function ($param_name)
                            function ($some, $param_name)
                            """
                    }
                ]
                for c_rule in controllable_param_rule:
                    c_rule_result = re.findall(re.escape(c_rule['rule']), param_block_code)
                    if len(c_rule_result) >= 1:
                        self.param_value = c_rule_result[0]
                        logging.info("R: True (New rule: controllable param: {0}, {1})".format(param_name, c_rule['example']))
                        return True
                logging.info("R: True")
                return True
            else:
                logging.info("R: False (Not contained $)")
                return False
        else:
            logging.warning("Not Found Param")

    def is_repair(self, repair_rule, block_repair):
        logging.info('--------- [3]. Is repair B:{0} ---------'.format(block_repair))
        code = self.block_code(block_repair)
        if code is False:
            logging.debug("R: Un Repair (repair code not match)")
            return False
        # replace repair {{PARAM}} const
        if '{{PARAM}}' in repair_rule:
            repair_rule = repair_rule.replace('{{PARAM}}', self.param_name)
        repair_result = re.findall(repair_rule, code)
        logging.debug(code)
        logging.debug(repair_result)
        if len(repair_result) >= 1:
            logging.debug("R: Repaired")
            return True
        else:
            logging.debug("R: Un Repair")
            return False


if __name__ == '__main__':
    try:
        parse = Parse('curl_setopt\s?\(.*,\s?CURLOPT_URL\s?,(.*)\)', '/Volumes/Statics/Project/Company/mogujie/appbeta/classes/crond/trade/chenxitest.php', '60', "curl_setopt($curl, CURLOPT_URL, $file); #output")
        if parse.is_controllable_param():
            parse.is_repair(r'$url', 2)
        else:
            print("UC")
    except Exception as e:
        print(traceback.print_exc())
