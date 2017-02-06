# -*- coding: utf-8 -*-

"""
    engine.core
    ~~~~~~~~~~~

    Implements core scan logic

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
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
        Initialize
        :param result: vulnerability info
                        {'task_id': self.task_id,
                        'project_id': self.project_id,
                        'rule_id': rule.id,
                        'result_id': result_id,
                        'file': file_path,
                        'line_number': line_number,
                        'code_content': code_content}
        :param rule: rule info
        :param project_name: project name
        :param white_list: white-list
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
        Is white-list file
        :return: boolean
        """
        return self.file_path.split(self.project_directory, 1)[1] in self.white_list

    def is_special_file(self):
        """
        Is special file
        :method: According to the file name to determine whether the special file
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
        Is test case file
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
        Whether only match the rules, do not parameter controllable processing
        :method: It is determined by judging whether the left and right sides of the regex_location are brackets
        :return: boolean
        """
        return self.rule_location[:1] == '(' and self.rule_location[-1] == ')'

    def is_annotation(self):
        """
        Is annotation
        :method: Judgment by matching comment symbols (skipped when self.is_match_only_rule condition is met)
               - PHP:  `#` `//` `\*` `*`
                    //asdfasdf
                    \*asdfasdf
                    #asdfasdf
                    *asdfasdf
               - Java:
        :return: boolean
        """
        match_result = re.findall(r"(#|\\\*|\/\/|\*)+", self.code_content)
        # Skip detection only on match
        if self.is_match_only_rule():
            return False
        else:
            return len(match_result) > 0

    def is_can_parse(self):
        """
        Whether to parse the parameter is controllable operation
        :return:
        """
        return self.file_path[-3:] == 'php' or self.file_path[-4:] == 'java'

    def push_third_party_vulnerabilities(self, vulnerabilities_id):
        """
        Pushed to a third-party vulnerability management platform
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
        Write a new vulnerability to the database
        :return:
        """
        vul = CobraResults(self.task_id, self.project_id, self.rule_id, self.file_path, self.line_number, self.code_content, self.repair_code, self.status)
        db.session.add(vul)
        db.session.commit()
        logging.info("insert new vulnerabilities Method: {0} VID: {1}".format(self.method, vul.id))
        self.push_third_party_vulnerabilities(vul.id)

    def process_vulnerabilities(self):
        """
        Process vulnerabilities
        Write vulnerabilities / change the vulnerability status / push third-party vulnerability management platform
        :return:
        """
        # default status
        if self.status is None:
            self.status = self.status_init

        # Handle relative paths
        self.file_path = self.file_path.replace(self.project_directory, '')

        # In scan
        if self.method == 0:
            """
            On Scan mode(method=1) only deal to new not fixed vulnerability(status=0)
            """
            if self.status == 0:
                # Check whether the unpatched vulnerability has been swept
                # Line number 0 when the search for special documents (not to bring the line number)
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

                # Not fixed vulnerabilities have not been swept before, is written to the vulnerability database
                if exist_result is None:
                    self.insert_vulnerabilities()
                else:
                    logging.debug("This vulnerabilities already exist!")
        elif self.method == 1:
            """
            On Repair (method=1)
            """
            if self.status == self.status_fixed:
                # View the original status of the vulnerability
                exist_result = CobraResults.query.filter_by(id=self.result_id).first()
                if exist_result is not None:
                    if exist_result.status < self.status_fixed:
                        # update vulnerability status is Fixed
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
        if self.is_white_list():
            logging.info("Whitelist file {0}".format(self.file_path))
            return False, 4000

        if self.is_special_file():
            logging.info("Special file: {0}".format(self.file_path))
            return False, 4001

        if self.is_test_file():
            logging.info("Test file: {0}".format(self.file_path))
            return False, 4007

        if self.is_annotation():
            logging.info("Annotation {0}".format(self.code_content))
            return False, 4002

        if self.is_match_only_rule():
            logging.info("Only Rule: {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # parameter is controllable
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
                        logging.info("parameter is not controllable")
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
        When the targeting rule is empty or the line number is 0, it means that this type of language (all suffixes in that language) is counted as a vulnerability
        Their repair method is only one: delete the file
        """
        if self.rule_location == '' or self.line_number == 0:
            logging.info("Find special files: RID{0}".format(self.rule_id))
            # Check if the file exists
            if os.path.isfile(self.file_path) is False:
                # If the file is not found, the vulnerability state is fixed
                logging.info("Deleted file repair is complete {0}".format(self.file_path))
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

        # Remove the trigger code (actual file)
        trigger_code = File(self.file_path).lines("{0}p".format(self.line_number))
        if trigger_code is False:
            logging.critical("Failed to fetch the trigger code {0}".format(self.code_content))
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
