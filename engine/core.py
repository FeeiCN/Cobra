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

        self.method = None

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
        vul = CobraResults(self.task_id, self.project_id, self.rule_id, self.file_path, self.line_number, self.code_content, self.status)
        db.session.add(vul)
        db.session.commit()
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
             1. 没有记录 (NotRecord)
                1.1 扫描结果是已修复 -> 跳过
                1.2 扫描结果是未修复 -> 写入

             2. 有记录是待修复(status<2)
                2.1 扫描结果是已修复 -> 更新
                2.2 扫描结果是未修复 -> 跳过

             3. 有记录是已修复(status=2)
                3.1 扫描结果是已修复 -> 跳过
                3.2 扫描结果是未修复 -> 写入
            """
            # 行号为0的时候则为搜索特殊文件
            if self.line_number == 0:
                exist_result = CobraResults.query.filter(
                    CobraResults.project_id == self.project_id,
                    CobraResults.rule_id == self.rule_id,
                    CobraResults.file == self.file_path,
                ).first()
            else:
                exist_result = CobraResults.query.filter(
                    CobraResults.project_id == self.project_id,
                    CobraResults.rule_id == self.rule_id,
                    CobraResults.file == self.file_path,
                    CobraResults.line == self.line_number,
                ).first()
            # 1. 没有记录
            if exist_result is None:
                # 1.1 扫描结果是已修复
                if self.status == 2:
                    # 跳过
                    pass
                # 1.2 扫描结果是未修复
                else:
                    # 写入
                    self.insert_vulnerabilities()
            # 2/3 有记录
            else:
                # 2. 有记录是待修复
                if exist_result.status < 2:
                    # 2.1 扫描结果是已修复
                    if self.status == 2:
                        # 更新
                        exist_result.status = 2
                        db.session.add(exist_result)
                        db.session.commit()
                    # 2.2 扫描结果是未修复
                    else:
                        # 跳过
                        pass
                # 3. 有记录是已修复
                else:
                    # 3.1 扫描结果是已修复
                    if self.status == 2:
                        # 跳过
                        pass
                    # 3.2 扫描结果是未修复
                    else:
                        # 写入
                        self.insert_vulnerabilities()
        # 修复状态下
        elif self.method == 1:
            """
            1. 待修复状态
               1.1 待修复 -> 跳过
               1.2 已修复 -> 更新

            2. 已修复状态(扫描时修复的)
               2.1 全部跳过
            """
            # 行号为0的时候则为搜索特殊文件
            if self.line_number == 0:
                exist_result = CobraResults.query.filter(
                    CobraResults.project_id == self.project_id,
                    CobraResults.rule_id == self.rule_id,
                    CobraResults.file == self.file_path,
                    CobraResults.status < 2
                ).first()
            else:
                exist_result = CobraResults.query.filter(
                    CobraResults.project_id == self.project_id,
                    CobraResults.rule_id == self.rule_id,
                    CobraResults.file == self.file_path,
                    CobraResults.line == self.line_number,
                    CobraResults.status < 2
                ).first()
            # 1. 待修复状态
            if exist_result is not None:
                # 1.2 已修复
                if self.status == 2:
                    exist_result.status = 2
                    db.session.add(exist_result)
                    db.session.commit()
                # 1.1 待修复,跳过
                else:
                    pass
            # 2. 已修复状态(没有数据)
            else:
                pass

        else:
            logging.critical("方法未初始化")

    def scan(self):
        """
        扫描漏洞
        :return:
        """
        self.method = 0
        # 白名单
        if self.is_white_list():
            logging.info("存在白名单列表中 {0}".format(self.file_path))
            return False, 4000

        # 特殊文件判断
        if self.is_special_file():
            logging.info("特殊文件 {0}".format(self.file_path))
            return False, 4001

        # 注释判断
        if self.is_annotation():
            logging.info("注释 {0}".format(self.code_content))
            return False, 4002

        # 仅匹配规则
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
                            logging.info("Static: repaired")
                            # 标记已修复
                            self.status = 2
                            self.process_vulnerabilities()
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
                self.code_content = self.code_content[:500] + '...'
            self.process_vulnerabilities()
            return True, 1002
        else:
            logging.critical("Exception core")
            return False, 4006

    def repair(self):
        """
        验证扫描到的漏洞是否修复
        :return: (Status, Result)
        """
        self.method = 1
        # 拼接绝对路径
        self.file_path = self.project_directory + self.file_path

        # 定位规则为空时或者行号为0,表示此类型语言(该语言所有后缀)文件都算作漏洞
        if self.rule_location == '' or self.line_number == 0:
            logging.info("Find special files: RID{0}".format(self.rule_id))
            # 检查文件是否存在
            if os.path.isfile(self.file_path) is False:
                # 未找到该文件则更新漏洞状态为已修复
                logging.info("已删除文件修复完成 {0}".format(self.file_path))
                self.status = self.status_fixed
                self.process_vulnerabilities()
                return True, 1001
            # 文件存在,漏洞还在
            return False, 4007

        # 取出触发代码(实际文件)
        trigger_code = File(self.file_path).lines("{0}p".format(self.line_number))
        if trigger_code is False:
            logging.critical("触发代码获取失败 {0}".format(self.code_content))
            return False, 4009
        self.code_content = trigger_code

        # 白名单
        if self.is_white_list():
            self.status = self.status_fixed
            self.process_vulnerabilities()
            logging.info("In white list {0}".format(self.file_path))
            return False, 4000

        # 特殊文件判断
        if self.is_special_file():
            self.status = self.status_fixed
            self.process_vulnerabilities()
            logging.info("Special File: {0}".format(self.file_path))
            return False, 4001

        # 注释判断
        if self.is_annotation():
            self.status = self.status_fixed
            self.process_vulnerabilities()
            logging.info("In Annotation {0}".format(self.code_content))
            return False, 4002

        # 仅匹配规则
        if self.is_match_only_rule():
            logging.info("Only match {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # 判断参数是否可控
            if self.is_can_parse() and self.rule_repair.strip() != '':
                try:
                    parse_instance = parse.Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                    if parse_instance.is_controllable_param():
                        if parse_instance.is_repair(self.rule_repair, self.block_repair):
                            logging.info("Static: repaired")
                            # 标记已修复
                            self.status = self.status_fixed
                            self.process_vulnerabilities()
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
                self.code_content = self.code_content[:500] + '...'
            self.process_vulnerabilities()
            return True, 1002
        else:
            logging.info("Not found")
            return False, 4006
