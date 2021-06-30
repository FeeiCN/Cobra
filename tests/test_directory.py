# -*- coding: utf-8 -*-

"""
    tests.test_directory
    ~~~~~~~~~~~~~~~~~~~~

    Tests pickup.directory

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
from cobra.config import project_directory
from cobra.pickup import Directory


def test_file():
    absolute_path = os.path.join(project_directory, 'cobra.py')
    files, file_sum, time_consume = Directory(absolute_path).collect_files()
    ext, ext_info = files[0]
    assert '.py' == ext
    assert 1 == ext_info['count']
    assert 'cobra.py' in ext_info['list']
    assert 1 == file_sum
    assert time_consume < 1


def test_directory():
    absolute_path = project_directory
    files, file_sum, time_consume = Directory(absolute_path).collect_files()
    assert len(files) > 1
