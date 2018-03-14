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
import xml.etree.ElementTree as eT
from cobra.detection import Detection
from cobra.config import project_directory


vul_path = project_directory+'/tests/vulnerabilities/'
examples_path = project_directory+'/tests/examples'


def test_framework():
    detection = Detection(vul_path+'requirements.txt', '.')
    frame = detection.framework
    assert frame == 'Flask'


def test_param_xml():
    detection = Detection(examples_path, '.')
    frame_data = {}
    language_data = {}
    tree = detection.rule()
    root = tree.getroot()
    frame_data, language_data = detection.parse_xml(root, frame_data, language_data)
    assert 'WordPress' in frame_data
    assert 'php' in language_data


def test_rule():
    detection = Detection(examples_path, '.')
    root = eT.ElementTree(file=examples_path+'/param_xml.xml')
    tree = detection.rule()
    assert type(root) is type(tree)


def test_get_dict():
    detection = Detection(examples_path, '.')
    extension = ['php', 'js', 'java']
    type_num = {}
    type_num = detection.get_dict(extension, type_num)
    print(type(type_num))
    assert type_num['php']['blank'] == 0


def test_project_information():
    extension = ['php', 'js', 'java']
    allfiles = Detection.project_information(examples_path, extension)
    assert examples_path+'/cloc.html' in allfiles


def test_count_py_line():
    count = Detection.count_py_line(examples_path+'/cloc.py')
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert count['count_code'] == 5


def test_count_php_line():
    count = Detection.count_php_line(examples_path+'/cloc.php')
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert count['count_code'] == 2


def test_count_java_line():
    count = Detection.count_java_line(examples_path+'/cloc.java')
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert count['count_code'] == 1


def test_count_html_line():
    count = Detection.count_html_line(examples_path+'/cloc.html')
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert count['count_code'] == 9


def test_count_data_line():
    count = Detection.count_data_line(examples_path+'/param_xml.xml')
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert count['count_code'] == 81


def test_countnum():
    count = {'count_blank': 10, 'count_code': 20, 'count_pound': 30}
    type_num = {'php': {'blank': 10, 'code': 10, 'pound': 10, 'files': 2}}
    ext = 'php'
    type_num = Detection.countnum(count, type_num, ext)
    assert 'php' in type_num


def test_count_total_num():
    type_num = {'php': {'blank': 10, 'code': 10, 'pound': 10, 'files': 2},
                'java': {'blank': 10, 'code': 10, 'pound': 10, 'files': 2}}
    extension = ['php', 'java']
    total_file = 0
    total_blank_line = 0
    total_pound_line = 0
    total_code_line = 0
    total_file, total_blank_line, total_pound_line, total_code_line = Detection.count_total_num(type_num, extension,
                                                                                                total_file,
                                                                                                total_blank_line,
                                                                                                total_pound_line,
                                                                                                total_code_line)
    assert isinstance(total_file, int)
    assert isinstance(total_blank_line, int)
    assert isinstance(total_pound_line, int)
    assert isinstance(total_code_line, int)


def test_cloc():
    assert Detection(examples_path, '.').cloc()
