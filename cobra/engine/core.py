# -*- coding: utf-8 -*-

"""
    engine.core
    ~~~~~~~~~~~

    Implements core scan logic

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import re
import traceback
from cobra.engine import parse
from cobra.pickup.file import File
from cobra.utils.config import Config
from cobra.utils.log import logger


class Core(object):
    def __init__(self, target_directory, vulnerability_result, single_rule, project_name, white_list, test=False, index=None):
        """
        Initialize
        :param: target_directory:
        :param: vulnerability_result:
        :param single_rule: rule info
        :param project_name: project name
        :param white_list: white-list
        :param test: is test
        :param index: vulnerability index
        """
        self.data = []

        self.target_directory = target_directory

        self.file_path = vulnerability_result.file_path.strip()
        self.line_number = vulnerability_result.line_number
        self.code_content = vulnerability_result.code_content.strip()

        self.rule_location = single_rule['match'].strip()
        self.rule_repair = single_rule['repair'].strip()
        self.block_repair = single_rule['block']

        self.project_name = project_name
        self.white_list = white_list
        self.test = test

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
        logger.info("""**Vulnerability({index})**
        > File: `{file}:{line}`
        > Code: `{code}`
        > Repair Code: `{repair}`""".format(
            index=index,
            file=self.file_path.replace(self.target_directory, ''),
            line=self.line_number,
            code=self.code_content,
            repair=self.repair_code))

    def is_white_list(self):
        """
        Is white-list file
        :return: boolean
        """
        return self.file_path.split(self.target_directory, 1)[1] in self.white_list

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

    def scan(self):
        """
        Scan vulnerabilities
        :flow:
        - whitelist file
        - special file
        - test file
        - annotation
        - rule
        :return: is_vulnerability, code
        """
        self.method = 0
        if self.is_white_list():
            logger.info("[RET] Whitelist")
            return False, 5001

        if self.is_special_file():
            logger.info("[RET] Special File")
            return False, 5002

        if self.is_test_file():
            logger.info("[RET] Test File")
            return True, 5003

        if self.is_annotation():
            logger.info("[RET] Annotation")
            return False, 5004

        if self.is_match_only_rule():
            logger.info("Only Rule: {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # parameter is controllable
            if self.is_can_parse() and self.rule_repair.strip() != '':
                try:
                    parse_instance = parse.Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                    param_is_controllable, data = parse_instance.is_controllable_param()
                    if param_is_controllable:
                        logger.info('[RET] Param is controllable')
                        is_repair, data = parse_instance.is_repair(self.rule_repair, self.block_repair)
                        if is_repair:
                            # fixed
                            logger.info('[RET] Vulnerability Fixed')
                            return False, 1002
                        else:
                            logger.info('Repair: Not fixed')
                            found_vul = True
                    else:
                        logger.info('[RET] Param Not Controllable')
                        return False, 4002
                except:
                    traceback.print_exc()
                    return False, 4004

        if found_vul:
            self.code_content = self.code_content.encode('unicode_escape')
            if len(self.code_content) > 512:
                self.code_content = self.code_content[:500]
            self.status = self.status_init
            self.repair_code = self.repair_code_init
            return True, 1001
        else:
            logger.info("[RET] Not found vulnerability")
            return False, 4002

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
        self.file_path = self.target_directory + self.file_path

        """
        When the targeting rule is empty or the line number is 0, it means that this type of language (all suffixes in that language) is counted as a vulnerability
        Their repair method is only one: delete the file
        """
        if self.rule_location == '' or self.line_number == 0:
            logger.info("Find special files: RID{0}".format(self.rule_id))
            # Check if the file exists
            if os.path.isfile(self.file_path) is False:
                # If the file is not found, the vulnerability state is fixed
                logger.info("Deleted file repair is complete {0}".format(self.file_path))
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
            logger.critical("Failed to fetch the trigger code {0}".format(self.code_content))
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
            logger.info("In white list {0}".format(self.file_path))
            return

        # Special file
        if self.is_special_file():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_special_file
            self.process_vulnerabilities()
            logger.info("Special File: {0}".format(self.file_path))
            return

        # Annotation
        if self.is_annotation():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_annotation
            self.process_vulnerabilities()
            logger.info("In Annotation {0}".format(self.code_content))
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
                    logger.info("Static: repaired")
                    # Fixed
                    self.status = self.status_fixed
                    self.repair_code = self.repair_code_fixed
                    self.process_vulnerabilities()
                    return
                else:
                    logger.critical("[repair] not fixed")
                    return
            except:
                logger.info(traceback.print_exc())
                return
