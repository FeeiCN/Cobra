# -*- coding: utf-8 -*-
import xml.etree.ElementTree as eT
from cobra.detection import Detection


def test_framework():
    detection = Detection('./examples/requirements.txt', '.')
    frame = detection.framework
    assert frame == 'Flask'


def test_param_xml():
    detection = Detection('./examples', '.')
    frame_data = {}
    language_data = {}
    tree = detection.rule()
    root = tree.getroot()
    frame_data, language_data = detection.parse_xml(root, frame_data, language_data)
    assert 'WordPress' in frame_data
    assert 'php' in language_data


def test_rule():
    detection = Detection('./example', '.')
    root = eT.ElementTree(file='./examples/param_xml.xml')
    tree = detection.rule()
    assert type(root) is type(tree)


def test_get_dict():
    detection = Detection('./example', '.')
    extension = ['php', 'js', 'java']
    type_num = {}
    type_num = detection.get_dict(extension, type_num)
    assert isinstance(extension, type(type_num.keys()))


def test_project_information():
    absolute_path = './examples'
    extension = ['php', 'js', 'java']
    allfiles = Detection.project_information(absolute_path, extension)
    assert './examples/wp-load.php' in allfiles


def test_count_py_line():
    count = Detection.count_py_line('./examples/cloc.py')
    type_ = count.keys()
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert type_ == type_count


def test_count_php_line():
    count = Detection.count_php_line('./examples/cloc.php')
    type_ = count.keys()
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert type_ == type_count


def test_count_java_line():
    count = Detection.count_java_line('./examples/cloc.java')
    type_ = count.keys()
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert type_ == type_count


def test_count_html_line():
    count = Detection.count_html_line('./examples/cloc.html')
    type_ = count.keys()
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert type_ == type_count


def test_count_data_line():
    count = Detection.count_data_line('./examples/param_xml.xml')
    type_ = count.keys()
    type_count = ['count_blank', 'count_code', 'count_pound']
    assert type_ == type_count


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
    assert Detection('./examples', '.').cloc()
