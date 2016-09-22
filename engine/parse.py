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
from pickup.file import File
from utils import log
import logging

log.Log()
logging = logging.getLogger(__name__)


class Parse:
    def __init__(self, rule, file_path, line, code):
        logging.info('###############################')
        self.rule = rule
        self.file_path = file_path
        self.line = line
        self.code = code
        self.param_name = None
        self.param_value = None

        logging.debug("\r\n 文件: {0}:{1} \r\n 定位: {2}\r\n 代码: {3}".format(self.file_path, self.line, self.rule, self.code))

        # 判断语言类型
        self.language = None
        languages = ['php', 'java']
        for language in languages:
            if self.file_path[-len(language):].lower() == language:
                self.language = language
        logging.debug('语言类型: {0}'.format(self.language))

        # 解析规则配置
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
                'assign_string': r"(\{0}\s?=\s?[\"'](.*)(?:['\"]))",
                'annotation': r"(#|\\\*|\/\/|\*)+"
            }
        }

    def functions(self):
        """
        获取该文件所有函数方法
        :return:
        """
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
        if self.language not in self.regex:
            logging.info("Undefined language's functions regex {0}".format(self.language))
            return False
        regex_functions = self.regex[self.language]['functions']
        param = [grep, "-n", "-r", "-P"] + [regex_functions, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = {}
            lines = str(result[0]).strip().split("\n")
            prev_function_name = ''
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    logging.info('Empty')
                    continue
                function = line.split(':')
                if len(function) < 2:
                    logging.info("没有找到分隔符(:)")

                regex_annotation = self.regex[self.language]['annotation']
                string = re.findall(regex_annotation, function[1].strip())
                if len(string) >= 1 and string[0] != '':
                    logging.info("该函数为注释行")

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
                    logging.info("无法找到函数名: {0}".format(line))
            end = sum(1 for l in open(self.file_path))
            for name, value in functions.items():
                if value['end'] is None:
                    functions[name]['end'] = end
            return functions
        else:
            return False

    def block_code(self, block_position):
        """
        获取搜索区块代码
        :param block_position:
                0:up 上
                1:down 下
                2:location_line 当前行
        :return:
        """
        if block_position == 2:
            if self.line is None or self.line == 0:
                logging.critical("行号异常: {0}".format(self.line))
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
                        logging.debug("触发行所在函数: {0} ({1} - {2}) {3}".format(function_name, function_value['start'], function_value['end'], in_this_function))
            else:
                # 没有functions时,以触发行来分割整个文件
                if block_position == 0:
                    block_start = 1
                    block_end = int(self.line) - 1
                elif block_position == 1:
                    block_start = int(self.line) + 1
                    block_end = sum(1 for l in open(self.file_path))
                logging.debug("没有找到任何方法,将以整个文件分割.")
            # get param block code
            line_rule = "{0},{1}p".format(block_start, block_end)
            code = File(self.file_path).lines(line_rule)
            logging.info('取出代码: {0} - {1}p'.format(block_start, block_end))
            return code

    def is_controllable_param(self):
        """
        参数是否可控
        :return:
        """
        param_name = re.findall(self.rule, self.code)
        if len(param_name) == 1:
            param_name = param_name[0].strip()
            param_name = re.escape(param_name)
            self.param_name = param_name
            logging.debug('参数: `{0}`'.format(param_name))
            # 固定字符串判断
            regex_string = self.regex[self.language]['string']
            string = re.findall(regex_string, param_name)
            if len(string) >= 1 and string[0] != '':
                logging.debug("是否字符串: 是")
                logging.info("返回: 不可控 (字符串)")
                return False
            logging.debug("是否字符串: 否")

            # 变量判断
            if param_name[:1] == '$':
                logging.debug("参数是否变量: 是")

                # 获取参数赋值代码块
                param_block_code = self.block_code(0)
                if param_block_code is False:
                    logging.debug("向上搜索参数区块代码: 未找到")
                    logging.info("返回: 可控 (代码未找到)")
                    return True
                logging.debug("向上搜索参数区块代码: {0}".format(param_block_code))

                # 外部取参赋值
                """
                # Need match
                $url = $_GET['test'];
                $url = $_POST['test'];
                $url = $_REQUEST['test'];
                $url = $_SERVER['user_agent'];
                # Don't match
                $url = $_SERVER
                $url = $testsdf;
                """
                regex_get_param = r'(\{0}\s*=\s*\$_[GET|POST|REQUEST|SERVER]+(?:\[))'.format(param_name)
                regex_get_param_result = re.findall(regex_get_param, param_block_code)
                if len(regex_get_param_result) >= 1:
                    self.param_value = regex_get_param_result[0]
                    logging.debug("参数是否直接取自外部: 是")
                    logging.info("返回: 可控(取外部入参)")
                    return True
                logging.debug("参数是否直接取自外部入参: 否")

                # 函数入参
                regex_function_param = r'(function\s*\w+\s*\(.*\{0})'.format(param_name)
                regex_function_param_result = re.findall(regex_function_param, param_block_code)
                if len(regex_function_param_result) >= 1:
                    self.param_value = regex_function_param_result[0]
                    logging.debug("参数是否函数入参: 是")
                    logging.info("返回: 可控(函数入参)")
                    return True
                logging.debug("参数是否直接函数入参: 否")

                # 常量赋值
                uc_rule = r'\{0}\s?=\s?([A-Z_]*)'.format(param_name)
                uc_rule_result = re.findall(uc_rule, param_block_code)
                if len(uc_rule_result) >= 1:
                    logging.debug("参数变量是否直接赋值常量: 是 `{0} = {1}`".format(param_name, uc_rule_result[0]))
                    logging.info("返回: 不可控")
                    return False
                logging.debug("参数变量是否直接赋值常量: 否")

                # 固定字符串判断
                regex_assign_string = self.regex[self.language]['assign_string'].format(param_name)
                string = re.findall(regex_assign_string, param_block_code)
                if len(string) >= 1 and string[0] != '':
                    logging.debug("是否赋值字符串: 是")
                    logging.info("返回: 不可控 (字符串)")
                    return False
                logging.debug("是否赋值字符串: 否")

                logging.info("返回: 可控(默认情况)")
                return True
            else:
                if self.language == 'java':
                    # Java 变量就是没有$
                    param_block_code = self.block_code(0)
                    if param_block_code is False:
                        logging.debug("向上搜索参数区块代码: 未找到")
                        logging.info("返回: 可控 (代码未找到)")
                        return True
                    logging.debug("向上搜索参数区块代码: {0}".format(param_block_code))
                    regex_assign_string = self.regex[self.language]['assign_string'].format(param_name)
                    string = re.findall(regex_assign_string, param_block_code)
                    if len(string) >= 1 and string[0] != '':
                        logging.debug("是否赋值字符串: 是")
                        logging.info("返回: 不可控 (字符串)")
                        return False
                    logging.debug("是否赋值字符串: 否")

                    # 是否取外部参数
                    regex_get_param = r'String\s{0}\s=\s\w+\.getParameter(.*)'.format(param_name)
                    get_param = re.findall(regex_get_param, param_block_code)
                    if len(get_param) >= 1 and get_param[0] != '':
                        logging.debug("是否赋值外部取参: 是")
                        logging.info("返回: 不可控 (外部取参)")
                        return False
                    logging.debug("是否赋值外部取参: 否")

                    logging.info("返回: 可控 (变量赋值)")
                    return True
                logging.debug("参数是否变量: 否 (没有包含$)")
                logging.info("返回: 不可控(参数不为变量)")
                return False
        else:
            logging.warning("未获取到参数名,请检查定位规则")

    def is_repair(self, repair_rule, block_repair):
        """
        是否已经修复
        :param repair_rule:
        :param block_repair:
        :return:
        """
        code = self.block_code(block_repair)
        if code is False:
            logging.debug("修复区块{0}代码: 未找到".format(block_repair))
            logging.info("返回: 未修复 (修复区块代码未找到)")
            return False
        # replace repair {{PARAM}} const
        if '{{PARAM}}' in repair_rule:
            repair_rule = repair_rule.replace('{{PARAM}}', self.param_name)
        logging.debug("修复区块({0})代码: {1}".format(block_repair, code))
        repair_result = re.findall(repair_rule, code)
        logging.debug("修复代码: {0}".format(repair_result))
        if len(repair_result) >= 1:
            logging.debug("修复结果: 已修复")
            return True
        else:
            logging.debug("修复结果: 未修复")
            return False
