# -*- coding: utf-8 -*-

"""
    tests.config
    ~~~~~~~~~~~~

    Tests utils.config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
from cobra.config import Config


def test_read_exception():
    value = Config('test', 'test').value
    assert value is None
