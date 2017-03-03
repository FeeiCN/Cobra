# -*- coding: utf-8 -*-

"""
    tests.common
    ~~~~~~~~~~~~

    Tests utils.common

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from utils import common


def test_convert_time():
    time = common.convert_time(129)
    assert time == '2\xe2\x80\xb29\xe2\x80\xb3'


def test_convert_number():
    number = common.convert_number(1234)
    assert number == '1,234'


def test_md5():
    md5 = common.md5('Cobra')
    assert md5 == 'd13eca1c700558f57d0310ef14277cc2'


def test_allowed_file():
    is_allowed = common.allowed_file('test01/test02/file.rar')
    assert is_allowed is True


def test_to_bool():
    test_bool = ['yes', 1, 'y', 'true', 't']
    for tb in test_bool:
        assert common.to_bool(tb) is True


def test_path_to_short():
    path = '/impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java'
    short_path = common.path_to_short(path)
    assert 'impl/src/.../utils/CertUtil.java' == short_path


def test_path_to_file():
    path = '/impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java'
    short_file = common.path_to_file(path)
    assert '.../CertUtil.java' == short_file


def test_percent():
    assert '20.0%' == common.percent(20, 100)


def test_format_gmt():
    assert '2016-09-14 17:57:41' == common.format_gmt('Wed, 14 Sep 2016 17:57:41 GMT')
