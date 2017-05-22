# -*- coding: utf-8 -*-

"""
    tests.test_directory
    ~~~~~~~~~~~~~~~~~~~~

    Tests pickup.directory

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
from cobra.utils.config import Config
from cobra.pickup.directory import Directory


def test_file():
    absolute_path = os.path.join(Config().project_directory, 'setup.py')
    files, file_sum, time_consume = Directory(absolute_path).collect_files()
    assert '.py' in files
    assert 1 == files['.py']['count']
    assert 'setup.py' == files['.py']['list'][0]
    assert 1 == file_sum
    assert time_consume < 1


def test_directory():
    absolute_path = Config().project_directory
    files, file_sum, time_consume = Directory(absolute_path).collect_files()
    assert '.yml' in files
    assert len(files) == 31
