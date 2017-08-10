# -*- coding: utf-8 -*-

"""
    tests.parser
    ~~~~~~~~~~~~

    Tests cobra.parser

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from cobra.parser import scan

tests = [
    (u"""<?php
    $cmd = $_GET['cmd'];
    system("ls" + $cmd);
    """, u'system', 3),
    (u"""<?php
    $cmd_test = $_POST['cmd'];
    exec("test" + $cmd_test);
    """, u'exec', 3),
]

tests_ret = [
    ('system', [u'$cmd'], '$_GET'),
    ('exec', [u'$cmd_test'], '$_POST'),
]


def test_param_controllable_assign():
    for index, test in enumerate(tests):
        test_content, func, line = test
        func, params, uc = scan(test_content, func, line)
        assert tests_ret[index][0] == func
        assert tests_ret[index][1] == params
        ret = False
        for param, value in uc.items():
            if param in params:
                if value['ic'] is True and value['cf'] == tests_ret[index][2]:
                    ret = True
        assert ret
