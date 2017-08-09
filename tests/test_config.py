# -*- coding: utf-8 -*-

"""
    tests.config
    ~~~~~~~~~~~~

    Tests utils.config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from cobra.config import Config


def test_read_exception():
    value = Config('test', 'test').value
    assert value is None
