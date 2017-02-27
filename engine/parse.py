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
from pickup.file import File
from utils.log import logging
from utils import tool

logging = logging.getLogger(__name__)


class Parse(object):
    def __init__(self, rule, file_path, line, code, ):
        self.data = []
        self.rule = rule
        self.file_path = file_path
        self.line = line
        self.code = code
        self.param_name = None
        self.param_value = None
        self.language = None
        languages = ['php', 'java']
        for language in languages:
            if self.file_path[-len(language):].lower() == language:
                self.language = language

        # Parse rule
        self.regex = {
            'java': {
                'functions': r'(?:public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(?:\{?|[^;])',
                'string': r"(?:[\"])(.*)(?:[\"])",
                'assign_string': r"String\s{0}\s=\s\"(.*)\";",
                'annotation': r"(\\\*|\/\/|\*)+"
            },
            'php': {
                'functions': r'(?:function\s+)(\w+)\s*\(',
                'string': r"(?:['\"])(.*)(?:[\"'])",
                'assign_string': r"({0}\s?=\s?[\"'](.*)(?:['\"]))",
                'annotation': r"(#|\\\*|\/\/|\*)+",
                'variable': r'(\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)',
                # Need match
                #    $url = $_GET['test'];
                #    $url = $_POST['test'];
                #    $url = $_REQUEST['test'];
                #    $url = $_SERVER['user_agent'];
                #    $v = trim($_GET['t']);
                # Don't match
                #    $url = $_SERVER
                #    $url = $testsdf;
                'assign_out_input': r'({0}\s?=\s?.*\$_[GET|POST|REQUEST|SERVER|COOKIE]+(?:\[))'
            }
        }
        self.log('debug', "Language: `{language}`".format(language=self.language))

    def log(self, level, message, test=True):
        if test:
            self.data.append('[{0}] {1}'.format(level.upper(), message))
        if level == 'critical':
            logging.critical(message)
        elif level == 'warning':
            logging.warning(message)
        elif level == 'info':
            logging.info(message)
        elif level == 'debug':
            logging.debug(message)
        elif level == 'error':
            logging.error(message)

    def functions(self):
        """
        get all functions in this file
        :return:
        """
        grep = tool.grep
        if self.language not in self.regex:
            self.log('info', "Undefined language's functions regex {0}".format(self.language))
            return False
        regex_functions = self.regex[self.language]['functions']
        param = [grep, "-s", "-n", "-r", "-P"] + [regex_functions, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = {}
            lines = str(result[0]).strip().split("\n")
            prev_function_name = ''
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    self.log('info', 'Empty')
                    continue
                function = line.split(':')
                if len(function) < 2:
                    self.log('info', "Not found(:)")

                regex_annotation = self.regex[self.language]['annotation']
                string = re.findall(regex_annotation, function[1].strip())
                if len(string) >= 1 and string[0] != '':
                    self.log('info', logging.info("This function is annotation"))

                function_name = re.findall(regex_functions, function[1].strip())
                if len(function_name) == 1:
                    function_name = function_name[0]
                    if index > 0 and prev_function_name in functions:
                        functions[prev_function_name]['end'] = function[0]
                    prev_function_name = function_name
                    functions[function_name] = {
                        'start': function[0],
                        'end': None  # next function's start
                    }
                else:
                    self.log('info', "Can't get function name: {0}".format(line))
            end = sum(1 for l in open(self.file_path))
            for name, value in functions.items():
                if value['end'] is None:
                    functions[name]['end'] = end
            return functions
        else:
            return False

    def block_code(self, block_position):
        """
        Get code block
        :param block_position:
                0:up
                1:down
                2:location_line
        :return:
        """
        if block_position == 2:
            if self.line is None or self.line == 0:
                self.log('critical', "Line exception: {0}".format(self.line))
                return False
            line_rule = '{0}p'.format(self.line)
            code = File(self.file_path).lines(line_rule)
            code = code.strip()
            return code
        else:
            block_start = 1
            block_end = 0
            functions = self.functions()
            if functions:
                for function_name, function_value in functions.items():
                    if int(function_value['start']) < int(self.line) < int(function_value['end']):
                        in_this_function = '<---- {0}'.format(self.line)
                        if block_position == 0:
                            block_start = function_value['start']
                            block_end = int(self.line) - 1
                        elif block_position == 1:
                            block_start = int(self.line)
                            block_end = int(function_value['end']) - 1
                        self.log('debug', "Trigger line's function name: {0} ({1} - {2}) {3}".format(function_name, function_value['start'], function_value['end'], in_this_function))
            else:
                if block_position == 0:
                    block_start = 1
                    block_end = int(self.line) - 1
                elif block_position == 1:
                    block_start = int(self.line) + 1
                    block_end = sum(1 for l in open(self.file_path))
                self.log('debug', "Not function anything `function`, will split file")
            # get param block code
            line_rule = "{0},{1}p".format(block_start, block_end)
            code = File(self.file_path).lines(line_rule)
            self.log('info', 'Get code: {0} - {1}p'.format(block_start, block_end))
            return code

    def is_controllable_param(self):
        """
        is controllable param
        :return:
        """
        self.log('info', '**Is controllable param**')
        param_name = re.findall(self.rule, self.code)
        if len(param_name) == 1:
            param_name = param_name[0].strip()
            self.param_name = param_name
            self.log('debug', 'Param: `{0}`'.format(param_name))
            # all is string
            regex_string = self.regex[self.language]['string']
            string = re.findall(regex_string, param_name)
            if len(string) >= 1 and string[0] != '':
                regex_get_variable_result = re.findall(self.regex[self.language]['variable'], param_name)
                len_regex_get_variable_result = len(regex_get_variable_result)
                if len_regex_get_variable_result >= 1:
                    # TODO
                    # 'ping $v1 $v2'
                    # foreach $vn
                    param_name = regex_get_variable_result[0]
                    self.log('info', "String's variables: `{variables}`".format(variables=','.join(regex_get_variable_result)))
                else:
                    self.log('debug', "String have variables: `No`")
                    return False, self.data
            self.log('debug', "String have variables: `Yes`")

            # variable
            if param_name[:1] == '$':
                self.log('debug', "Is variable: `Yes`")

                # Get assign code block
                param_block_code = self.block_code(0)
                if param_block_code is False:
                    self.log('debug', "Can't get assign code block")
                    return True, self.data
                self.log('debug', 'Code assign code block: ```{language}\r\n{block}```'.format(language=self.language, block=param_block_code))

                # Is assign out input
                regex_get_param = self.regex[self.language]['assign_out_input'].format(re.escape(param_name))
                regex_get_param_result = re.findall(regex_get_param, param_block_code)
                if len(regex_get_param_result) >= 1:
                    self.param_value = regex_get_param_result[0]
                    self.log('debug', "Is assign out input: `Yes`")
                    return True, self.data
                self.log('debug', "Is assign out input: `No`")

                # Is function's param
                regex_function_param = r'(function\s*\w+\s*\(.*{0})'.format(re.escape(param_name))
                regex_function_param_result = re.findall(regex_function_param, param_block_code)
                if len(regex_function_param_result) >= 1:
                    self.param_value = regex_function_param_result[0]
                    self.log('debug', "Is function's param: `Yes`")
                    return True, self.data
                self.log('debug', "Is function's param: `No`")

                # Is assign CONST
                uc_rule = r'{0}\s?=\s?([A-Z_]*)'.format(re.escape(param_name))
                uc_rule_result = re.findall(uc_rule, param_block_code)
                if len(uc_rule_result) >= 1:
                    self.log('debug', "Is assign CONST: Yes `{0} = {1}`".format(param_name, uc_rule_result[0]))
                    return False, self.data
                self.log('debug', "Is assign CONST: `No`")

                # Is assign string
                regex_assign_string = self.regex[self.language]['assign_string'].format(re.escape(param_name))
                string = re.findall(regex_assign_string, param_block_code)
                if len(string) >= 1 and string[0] != '':
                    self.log('debug', "Is assign string: `Yes`")
                    return False, self.data
                self.log('debug', "Is assign string: `No`")
                return True, self.data
            else:
                if self.language == 'java':
                    # Java variable didn't have `$`
                    param_block_code = self.block_code(0)
                    if param_block_code is False:
                        self.log('debug', "Can't get block code")
                        return True, self.data
                    self.log('debug', "Block code: ```{language}\r\n{code}```".format(language=self.language, code=param_block_code))
                    regex_assign_string = self.regex[self.language]['assign_string'].format(re.escape(param_name))
                    string = re.findall(regex_assign_string, param_block_code)
                    if len(string) >= 1 and string[0] != '':
                        self.log('debug', "Is assign string: `Yes`")
                        return False, self.data
                    self.log('debug', "Is assign string: `No`")

                    # Is assign out data
                    regex_get_param = r'String\s{0}\s=\s\w+\.getParameter(.*)'.format(re.escape(param_name))
                    get_param = re.findall(regex_get_param, param_block_code)
                    if len(get_param) >= 1 and get_param[0] != '':
                        self.log('debug', "Is assign out data: `Yes`")
                        return False, self.data
                    self.log('debug', "Is assign out data: `No`")
                    return True, self.data
                self.log('info', "Not Java/PHP, can't parse")
                return False, self.data
        else:
            self.log('warning', "Can't get `param`, check built-in rule")

    def is_repair(self, repair_rule, block_repair):
        """
        Is repair
        :param repair_rule:
        :param block_repair:
        :return:
        """
        self.data = []
        self.log('info', '**Is Repair**')
        block_repair_desc = {
            0: 'UP',
            1: 'DOWN',
            2: 'CURRENT'
        }
        self.log('debug', 'Block code: {block}'.format(block=block_repair_desc[block_repair]))
        code = self.block_code(block_repair)
        if code is False:
            self.log('debug', "Can't get repair block code")
            return False, self.data
        # replace repair {{PARAM}} const
        if '{{PARAM}}' in repair_rule:
            repair_rule = repair_rule.replace('{{PARAM}}', self.param_name)
        self.log('debug', "Block code: {code}".format(code=code))
        repair_result = re.findall(repair_rule, code)
        self.log('debug', "Repair code: {0}".format(repair_result))
        if len(repair_result) >= 1:
            return True, self.data
        else:
            return False, self.data
