# -*- coding: utf-8 -*-

"""
    engine.rule
    ~~~~~~~~~~~

    Implements rule test

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import re


class Rule(object):
    NEWLINE = '\n'
    SPLIT_TYPE = '---'
    SPLIT_RULE = '***'
    COMMENT = '#'

    def __init__(self, rule_location, rule_repair, verify_content):
        self.rule_location = rule_location
        self.rule_repair = rule_repair
        self.verify_content = verify_content.strip()

        self.data = {}

    def verify(self):
        # current mode
        mode = 'MATCHED'
        if self.verify_content == '':
            return self.data
        lines = self.verify_content.split(self.NEWLINE)
        for index, line in enumerate(lines):
            if self.SPLIT_TYPE in line:
                mode = 'NOT_MATCHED'
            if self.COMMENT not in line and self.SPLIT_TYPE not in line and self.SPLIT_RULE not in line:
                not_matched = mode == 'NOT_MATCHED'
                self.data[index] = self.verify_check(line, not_matched)
        return self.data

    def verify_check(self, test_rule, reverse=False):
        regex_test_rule = re.findall(self.rule_location, test_rule)
        ret = len(regex_test_rule) >= 1
        if reverse:
            if ret:
                return False
            else:
                return True
        else:
            return ret
