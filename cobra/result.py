# -*- coding: utf-8 -*-

"""
    result
    ~~~~~~

    Implements result structure

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""


class VulnerabilityResult:
    def __init__(self):
        self.vulnerability = ''
        self.rule_name = ''
        self.file_path = None
        self.line_number = None
        self.code_content = None
        self.match_result = None
<<<<<<< HEAD
        self.author = None
        self.timestamp = None
        self.id = None
        self.mode = None
        self.type = None

    def convert_to_dict(self):
        _dict = {}
        _dict.update(self.__dict__)
        return _dict
=======
        self.commit_time = None
        self.commit_author = 'Unknown'
>>>>>>> bcaa60ec448180b5eacbed7da521e889c3b6d1e2
