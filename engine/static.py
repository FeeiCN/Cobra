#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
from engine import rules


def scan(code, language):
    if language == 'php':
        return scan_php(code)
    elif language == 'java':
        return scan_php(code)
    else:
        return 'not support language:' + language


def scan_php(code):
    functions = rules.php_function()
    for func in functions:
        if func in code:
            return 1
    return 0
