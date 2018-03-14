# -*- coding: utf-8 -*-

"""
    tests.common
    ~~~~~~~~~~~~

    Tests utils.common

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
from cobra.utils import *


def test_convert_time():
    assert convert_time(129) == '2\'9"'


def test_convert_time_err():
    assert convert_time(0) == '0"'


def test_convert_number():
    assert convert_number(1234) == '1,234'


def test_convert_number_0():
    assert convert_number(0) == '0'


def test_convert_number_none():
    assert convert_number(None) == '0'


def test_md5():
    assert md5('Cobra') == 'd13eca1c700558f57d0310ef14277cc2'


def test_allowed_file():
    pass


def test_to_bool():
    test_bool = ['yes', 1, 'y', 'true', 't']
    for tb in test_bool:
        assert to_bool(tb) is True


def test_path_to_short():
    path = '/impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java'
    short_path = path_to_short(path)
    assert 'impl/src/.../utils/CertUtil.java' == short_path


def test_path_to_file():
    path = '/impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java'
    short_file = path_to_file(path)
    assert '.../CertUtil.java' == short_file


def test_percent():
    assert percent(20, 100) == '20.0%'


def test_format_gmt():
    assert format_gmt('Wed, 14 Sep 2016 17:57:41 GMT') == '2016-09-14 17:57:41'


def test_split_branch():
    target_str = 'https://github.com/test/test.git:dev'
    target, branch = split_branch(target_str)
    assert target == 'https://github.com/test/test.git'
    assert branch == 'dev'
    target_str = 'https://github.com/test/test.git'
    target, branch = split_branch(target_str)
    assert target == 'https://github.com/test/test.git'
    assert branch == 'master'


def test_secure_filename():
    assert secure_filename(u'正则.测试.md') == u'正则.测试.md'
    assert secure_filename('../../../etc/passwd').count('/') == 0
