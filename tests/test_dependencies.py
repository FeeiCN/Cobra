#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import xml.etree.ElementTree as eT
from cobra.dependencies import Dependencies


def test_find_file():
    dependencies = Dependencies('./examples/requirements.txt')
    file_path, flag = dependencies.find_file()
    assert isinstance(file_path, list)
    assert isinstance(flag, int)


def test_get_path():
    dependencies = Dependencies('./examples/requirements.txt')
    for root, dirs, filenames in os.walk(dependencies.directory):
        for filename in filenames:
            file_path = dependencies.get_path(root, filename)
            assert isinstance(file_path, list)


def test_find_python_pip():
    dependencies = Dependencies('./examples/requirements.txt')
    dependencies.dependencies()
    assert 'Flask' in dependencies.get_result


def test_find_java_mvn():
    dependencies = Dependencies('./examples/pom.xml')
    dependencies.dependencies()
    assert 'pom-manipulation-io' in dependencies.get_result


def test_parse_xml():
    dependencies = Dependencies('./examples/pom.xml')
    root = dependencies.parse_xml('./examples/pom.xml')
    root_test = eT.parse('./examples/pom.xml')
    assert isinstance(root, type(root_test))


def test_get_version():
    dependencies = Dependencies('./examples/requirements.txt')
    dependencies.dependencies()
    version = dependencies.get_version('Flask')
    assert version == '0.10.1'


def test_get_result():
    dependencies = Dependencies('./examples/requirements.txt')
    dependencies.dependencies()
    result = dependencies.get_result
    assert isinstance(result, dict)
