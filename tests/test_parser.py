#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Tests cobra.parser

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
from cobra.parser import scan_parser
from cobra.config import project_directory


target_projects = project_directory + '/tests/examples/v_parser.php'
with open(target_projects, 'r') as fi:
    code_contents = fi.read()

sensitive_func = ['system']
repairs = []
lineno = 7


def test_scan_parser():
    assert scan_parser(code_contents, sensitive_func, lineno, repairs)
