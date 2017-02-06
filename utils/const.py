# -*- coding: utf-8 -*-

"""
    utils.const
    ~~~~~~~~~~~

    Implements const

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""


class Vulnerabilities:
    def __init__(self, key):
        self.key = key

    def status_description(self):
        status = {
            0: 'Not fixed',
            1: 'Not fixed(Push third-party)',
            2: 'Fixed'
        }
        if self.key in status:
            return status[self.key]
        else:
            return False

    def repair_description(self):
        repair = {
            0: 'Initialize',
            1: 'Fixed',
            4000: 'File not exist',
            4001: 'Special file',
            4002: 'Whitelist',
            4003: 'Test file',
            4004: 'Annotation',
            4005: 'Modify code',
            4006: 'Empty code',
            4007: 'Const file',
            4008: 'Third-party'
        }
        if self.key in repair:
            return repair[self.key]
        else:
            return False

    def level_description(self):
        level = {
            0: 'Undefined',
            1: 'Low',
            2: 'Medium',
            3: 'High',
        }
        if self.key in level:
            return level[self.key]
        else:
            return False
