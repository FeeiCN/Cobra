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
import os
import re
import logging
import traceback
from engine import parse
from pickup.file import File
from app import db, CobraResults
from utils.queue import Queue
from utils.config import Config

logging = logging.getLogger(__name__)


class Core:
    def __init__(self, result, rule, project_name, white_list):
        """
        初始化
        :param result: 漏洞信息
                        {'task_id': self.task_id,
                        'project_id': self.project_id,
                        'rule_id': rule.id,
                        'result_id': result_id,
                        'file': file_path,
                        'line_number': line_number,
                        'code_content': code_content}
        :param rule: 规则信息
        :param project_name: 项目名称
        :param white_list: 白名单列表
        """
        self.project_id = result['project_id']
        self.project_directory = result['project_directory']
        self.rule_id = result['rule_id']
        self.task_id = result['task_id']
        self.result_id = result['result_id']

        self.third_party_vulnerabilities_name = result['third_party_vulnerabilities_name']
        self.third_party_vulnerabilities_type = result['third_party_vulnerabilities_type']

        self.file_path = result['file_path'].strip()
        self.line_number = result['line_number']
        self.code_content = result['code_content'].strip()

        self.rule_location = rule.regex_location.strip()
        self.rule_repair = rule.regex_repair.strip()
        self.block_repair = rule.block_repair

        self.project_name = project_name
        self.white_list = white_list

        self.status = None
        self.status_init = 0
        self.status_fixed = 2

        # const.py
        self.repair_code = None
        self.repair_code_init = 0
        self.repair_code_fixed = 1
        self.repair_code_not_exist_file = 4000
        self.repair_code_special_file = 4001
        self.repair_code_whitelist = 4002
        self.repair_code_test_file = 4003
        self.repair_code_annotation = 4004
        self.repair_code_modify = 4005
        self.repair_code_empty_code = 4006
        self.repair_code_const_file = 4007
        self.repair_code_third_party = 4008

        self.method = None

    def is_white_list(self):
        """
        是否是白名单文件
        :return: boolean
        """
        return self.file_path.split(self.project_directory, 1)[1] in self.white_list

    def is_special_file(self):
        """
        是否是特殊文件
        :method: 通过判断文件名中是否包含.min.js来判定
        :return: boolean
        """
        special_paths = [
            '/node_modules/',
            '/bower_components/',
            '.min.js',
        ]
        for path in special_paths:
            if path in self.file_path:
                return True
        return False

    def is_test_file(self):
        """
        is test case file
        :method: file name
        :return: boolean
        """
        test_paths = [
            '/test/',
            '/tests/',
            '/unitTests/'
        ]
        for path in test_paths:
            if path in self.file_path:
                return True
        return False

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
               - PHP:  `#` `//` `\*` `*`
                    //asdfasdf
                    \*asdfasdf
                    #asdfasdf
                    *asdfasdf
               - Java:
        :return: boolean
        """
        match_result = re.findall(r"(#|\\\*|\/\/|\*)+", self.code_content)
        # 仅仅匹配时跳过检测
        if self.is_match_only_rule():
            return False
        else:
            return len(match_result) > 0

    def is_can_parse(self):
        """
        是否可以进行解析参数是否可控的操作
        :return:
        """
        return self.file_path[-3:] == 'php' or self.file_path[-4:] == 'java'

    def push_third_party_vulnerabilities(self, vulnerabilities_id):
        """
        推送到第三方漏洞管理平台
        :param vulnerabilities_id:
        :return:
        """
        try:
            status = Config('third_party_vulnerabilities', 'status').value
            if int(status):
                q = Queue(self.project_name, self.third_party_vulnerabilities_name, self.third_party_vulnerabilities_type, self.file_path, self.line_number, self.code_content, vulnerabilities_id)
                q.push()
        except Exception as e:
            print(traceback.print_exc())
            logging.critical(e.message)

    def insert_vulnerabilities(self):
        """
        写入新漏洞
        :return:
        """
        vul = CobraResults(self.task_id, self.project_id, self.rule_id, self.file_path, self.line_number, self.code_content, self.repair_code, self.status)
        db.session.add(vul)
        db.session.commit()
        logging.info("insert new vulnerabilities Method: {0} VID: {1}".format(self.method, vul.id))
        self.push_third_party_vulnerabilities(vul.id)

    def process_vulnerabilities(self):
        """
        处理漏洞
        写入漏洞/更改漏洞状态/推送第三方漏洞管理平台
        :return:
        """
        # 默认状态
        if self.status is None:
            self.status = self.status_init

        # 处理相对路径
        self.file_path = self.file_path.replace(self.project_directory, '')

        # 扫描状态下
        if self.method == 0:
            """
            Scan下(method=1)只会有新增的未修复的漏洞(status=0)
            """
            if self.status == 0:
                # 检查该未修复的漏洞是否已经扫到过
                # 行号为0的时候则为搜索特殊文件(不用带上行号)
                if self.line_number == 0:
                    exist_result = CobraResults.query.filter(
                        CobraResults.project_id == self.project_id,
                        CobraResults.rule_id == self.rule_id,
                        CobraResults.file == self.file_path,
                    ).order_by(CobraResults.id.desc()).first()
                else:
                    exist_result = CobraResults.query.filter(
                        CobraResults.project_id == self.project_id,
                        CobraResults.rule_id == self.rule_id,
                        CobraResults.file == self.file_path,
                        CobraResults.line == self.line_number,
                    ).order_by(CobraResults.id.desc()).first()

                # 该未修复的漏洞之前没有扫到过,则写入漏洞库
                if exist_result is None:
                    self.insert_vulnerabilities()
                else:
                    logging.debug("This vulnerabilities already exist!")
        elif self.method == 1:
            """
            Repair下(method=1)只有处理已修复的漏洞
            """
            if self.status == self.status_fixed:
                # 查看漏洞原始状态
                exist_result = CobraResults.query.filter_by(id=self.result_id).first()
                if exist_result is not None:
                    if exist_result.status < self.status_fixed:
                        # 更新漏洞状态为已修复
                        exist_result.status = self.status_fixed
                        exist_result.repair = self.repair_code
                        db.session.add(exist_result)
                        db.session.commit()
                    else:
                        logging.critical("Vulnerabilities status not < fixed")
                else:
                    logging.critical("Not found vulnerabilities on repair method")
        else:
            logging.critical("Core method not initialize")

    def scan(self):
        """
        Scan vulnerabilities
        :flow:
        - whitelist file
        - special file
        - test file
        - annotation
        - rule
        :return:
        """
        self.method = 0
        # Whitelist file
        if self.is_white_list():
            logging.info("Whitelist file {0}".format(self.file_path))
            return False, 4000

        # Special file
        if self.is_special_file():
            logging.info("Special file: {0}".format(self.file_path))
            return False, 4001

        # Test file
        if self.is_test_file():
            logging.info("Test file: {0}".format(self.file_path))
            return False, 4007

        # Annotation
        if self.is_annotation():
            logging.info("Annotation {0}".format(self.code_content))
            return False, 4002

        # Only location rule
        if self.is_match_only_rule():
            logging.info("仅匹配规则 {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # 判断参数是否可控
            if self.is_can_parse() and self.rule_repair.strip() != '':
                try:
                    parse_instance = parse.Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                    if parse_instance.is_controllable_param():
                        if parse_instance.is_repair(self.rule_repair, self.block_repair):
                            # fixed
                            return True, 1003
                        else:
                            found_vul = True
                    else:
                        logging.info("参数不可控")
                        return False, 4004
                except:
                    print(traceback.print_exc())
                    return False, 4005

        if found_vul:
            self.code_content = self.code_content.encode('unicode_escape')
            if len(self.code_content) > 512:
                self.code_content = self.code_content[:500]
            self.status = self.status_init
            self.repair_code = self.repair_code_init
            self.process_vulnerabilities()
            return True, 1002
        else:
            logging.info("Not found vulnerabilities")
            return False, 4006

    def repair(self):
        """
        Scan vulnerabilities is repair
        :flow:
        - exist file [add]
        - test file
        - whitelist file
        - special file
        - annotation
        - rule
        :return: (Status, Result)
        """
        self.method = 1

        # Full path
        self.file_path = self.project_directory + self.file_path

        """
        定位规则为空时或者行号为0,表示此类型语言(该语言所有后缀)文件都算作漏洞
        他们的修复方法只有一个:删除文件
        """
        if self.rule_location == '' or self.line_number == 0:
            logging.info("Find special files: RID{0}".format(self.rule_id))
            # 检查文件是否存在
            if os.path.isfile(self.file_path) is False:
                # 未找到该文件则更新漏洞状态为已修复
                logging.info("已删除文件修复完成 {0}".format(self.file_path))
                self.status = self.status_fixed
                self.repair_code = self.repair_code_not_exist_file
                self.process_vulnerabilities()
                return
            else:
                return

        # Not exist file
        if os.path.isfile(self.file_path) is False:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_not_exist_file
            self.process_vulnerabilities()
            return

        # Test file
        if self.is_test_file():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_test_file
            self.process_vulnerabilities()
            return

        """
        Cobra Skip

        @cobra const
        `@[cC][oO][bB][rR][aA]\s*[cC][oO][nN][sS][tT]`
        """
        file_content = File(self.file_path).read_file()
        ret_regex_const = re.findall(r'@[cC][oO][bB][rR][aA]\s*[cC][oO][nN][sS][tT]', file_content)
        if len(ret_regex_const) > 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_const_file
            self.process_vulnerabilities()
            return

        """
        @cobra third-party
        `@[cC][oO][bB][rR][aA]\s*[tT][hH][iI][rR][dD]-[pP][aA][rR][tT][yY]`
        """
        ret_regex_third_party = re.findall(r'@[cC][oO][bB][rR][aA]\s*[tT][hH][iI][rR][dD]-[pP][aA][rR][tT][yY]', file_content)
        if len(ret_regex_third_party) > 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_third_party
            self.process_vulnerabilities()
            return

        # 取出触发代码(实际文件)
        trigger_code = File(self.file_path).lines("{0}p".format(self.line_number))
        if trigger_code is False:
            logging.critical("触发代码获取失败 {0}".format(self.code_content))
            self.status = self.status_fixed
            self.repair_code = self.repair_code_empty_code
            self.process_vulnerabilities()
            return

        self.code_content = trigger_code

        # Whitelist
        if self.is_white_list():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_whitelist
            self.process_vulnerabilities()
            logging.info("In white list {0}".format(self.file_path))
            return

        # Special file
        if self.is_special_file():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_special_file
            self.process_vulnerabilities()
            logging.info("Special File: {0}".format(self.file_path))
            return

        # Annotation
        if self.is_annotation():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_annotation
            self.process_vulnerabilities()
            logging.info("In Annotation {0}".format(self.code_content))
            return

        # Modify
        ret_regex = re.findall(self.rule_location, trigger_code.strip())
        if len(ret_regex) == 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_modify
            self.process_vulnerabilities()
            return

        # Fixed
        if self.is_can_parse() and self.rule_repair.strip() != '':
            try:
                parse_instance = parse.Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                if parse_instance.is_repair(self.rule_repair, self.block_repair):
                    logging.info("Static: repaired")
                    # Fixed
                    self.status = self.status_fixed
                    self.repair_code = self.repair_code_fixed
                    self.process_vulnerabilities()
                    return
                else:
                    logging.critical("[repair] not fixed")
                    return
            except:
                logging.info(traceback.print_exc())
                return
