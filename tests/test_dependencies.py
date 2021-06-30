#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import xml.etree.ElementTree as eT
from cobra.dependencies import Dependencies
from cobra.config import project_directory


requirements = project_directory+'/tests/vulnerabilities/requirements.txt'
pom = project_directory+'/tests/vulnerabilities/pom.xml'


def test_find_file():
    dependencies = Dependencies(requirements)
    file_path, flag = dependencies.find_file()
    assert isinstance(file_path, list)
    assert isinstance(flag, int)


def test_get_path():
    dependencies = Dependencies(requirements)
    for root, dirs, filenames in os.walk(dependencies.directory):
        for filename in filenames:
            file_path = dependencies.get_path(root, filename)
            assert isinstance(file_path, list)


def test_find_python_pip():
    dependencies = Dependencies(requirements)
    dependencies.dependencies()
    assert 'Flask' in str(dependencies.get_result)


def test_find_java_mvn():
    dependencies = Dependencies(pom)
    dependencies.dependencies()
    assert 'pom-manipulation-io' in str(dependencies.get_result)


def test_parse_xml():
    dependencies = Dependencies(pom)
    root = dependencies.parse_xml(pom)
    root_test = eT.parse(pom)
    assert isinstance(root, type(root_test))


def test_get_version():
    dependencies = Dependencies(requirements)
    dependencies.dependencies()
    version = dependencies.get_version('Flask-Migrate')
    assert '1.8.0' in version


def test_get_result():
    dependencies = Dependencies(requirements)
    dependencies.dependencies()
    result = dependencies.get_result
    assert isinstance(result, dict)
