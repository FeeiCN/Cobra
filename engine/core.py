# -*- coding: utf-8 -*-

"""
    engine.core
    ~~~~~~~~~~~

    Implements core scan logic

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import re
import logging
import traceback
from engine import parse

logging = logging.getLogger(__name__)


class Core:
    def __init__(self, file_path, line_number, code_content, rule_location, rule_repair, block_repair, white_list):
        """
        初始化
        :param file_path: 文件绝对路径
        :param line_number: 定位规则触发行数
        :param code_content: 代码内容
        :param rule_location: 定位规则
        :param rule_repair: 修复规则
        :param block_repair: 验证修复区块
        :param white_list: 白名单列表
        """
        self.file_path = file_path.strip()
        self.line_number = line_number
        self.code_content = code_content.strip()
        self.rule_location = rule_location.strip()
        self.rule_repair = rule_repair.strip()
        self.block_repair = block_repair
        self.white_list = white_list
        logging.debug("{0} {1} {2} {3} {4} {5}".format(self.file_path, self.line_number, self.code_content, self.rule_location, self.rule_repair, self.block_repair))

    def is_white_list(self):
        """
        是否是白名单文件
        :return: boolean
        """
        return self.file_path in self.white_list

    def is_special_file(self):
        """
        是否是特殊文件
        :method: 通过判断文件名中是否包含.min.js来判定
        :return: boolean
        """
        return ".min.js" in self.file_path

    def is_match_only_rule(self):
        """
        是否仅仅匹配规则,不做参数可控处理
        :method: 通过判断定位规则(regex_location)的左右两边是否是括号来判定
        :return: boolean
        """
        return self.rule_location[:1] == '(' and self.rule_location[-1] == ')'

    def is_annotation(self):
        """
        是否是注释
        :method: 通过匹配注释符号来判定 (当符合self.is_match_only_rule条件时跳过)
                    PHP: `#` `//` `/*` `*`
        :return: boolean
        """
        match_result = re.match("(#)?(//)?(\*)?(/\*)?", self.code_content)
        return match_result.group(0) is not None and match_result.group(0) is not "" and self.is_match_only_rule() is not True

    def analyse(self):
        """
        通过规则分析漏洞
        :return: (Status, Result)
        """
        # 定位规则为空时,表示此类型语言(该语言所有后缀)文件都算作漏洞
        if self.rule_location == '':
            result = {
                'file_path': self.file_path,
                'line_number': 0,
                'code': '',
                'status': 0
            }
            return True, result

        # 白名单
        if self.is_white_list():
            logging.info("In white list {0}".format(self.file_path))
            return False, 4000

        # 特殊文件判断
        if self.is_special_file():
            logging.info("Special File: {0}".format(self.file_path))
            return False, 4001

        # 注释判断
        if self.is_annotation():
            logging.info("In Annotation {0}".format(self.code_content))
            return False, 4002

        param_value = None

        # 仅匹配规则
        if self.is_match_only_rule():
            logging.info("Only match {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # 判断参数是否可控
            if self.file_path[-3:] == 'php' and self.rule_repair.strip() != '':
                try:
                    parse_instance = parse.Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                    if parse_instance.is_controllable_param():
                        if parse_instance.is_repair(self.rule_repair, self.block_repair):
                            logging.info("Static: repaired")
                            return False, 4003
                        else:
                            if parse_instance.param_value is not None:
                                param_value = parse_instance.param_value
                            found_vul = True
                    else:
                        logging.info("Static: uncontrollable param")
                        return False, 4004
                except:
                    print(traceback.print_exc())
                    return False, 4005

        if found_vul:
            code_content = self.code_content.encode('unicode_escape')
            if len(code_content) > 512:
                code_content = code_content[:500] + '...'
            code_content = '# Trigger\r{0}'.format(code_content)
            if param_value is not None:
                code_content = '# Param\r{0}\r//\r// ------ Continue... ------\r//\r{1}'.format(param_value, code_content)

            result = {
                'file_path': self.file_path,
                'line_number': self.line_number,
                'code_content': code_content,
                'status': 0
            }
            return True, result
        else:
            print("Exception core")
