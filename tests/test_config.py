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
import pytest
from utils.config import Config


def test_read_exception():
    with pytest.raises(SystemExit):
        value = Config('test', 'test').value
        assert value == 0


def test_read_normal():
    value = Config('upload', 'extensions').value
    assert 'rar' in value
