# -*- coding: utf-8 -*-
import unittest
import xml.etree.ElementTree as eT
from cobra.detection import Detection


class TestDetection(unittest.TestCase):
    def test_framework(self):
        detection = Detection('./examples', '.')
        frame = detection.framework()
        self.assertIs(frame, None)

    def test_param_xml(self):
        detection = Detection('./examples', '.')
        frame_data = {}
        language_data = {}
        tree = detection.rule()
        root = tree.getroot()
        frame_data, language_data = detection.parse_xml(root, frame_data, language_data)
        self.assertTrue(frame_data.has_key('WordPress'))
        self.assertTrue(language_data.has_key('php'))

    def test_rule(self):
        detection = Detection('./example', '.')
        root = eT.ElementTree(file='./examples/param_xml.xml')
        tree = detection.rule()
        self.assertIs(type(root), type(tree))

    def test_get_dict(self):
        detection = Detection('./example', '.')
        extension = ['php', 'js', 'java']
        type_num = {}
        type_num = detection.get_dict(extension, type_num)
        self.assertIs(type(extension), type(type_num.keys()))

    def test_project_information(self):
        absolute_path = './examples'
        extension = ['php', 'js', 'java']
        allfiles = Detection.project_information(absolute_path, extension)
        self.assertIn('./examples/wp-load.php', allfiles)

    def test_count_py_line(self):
        count = Detection.count_py_line('./examples/cloc.py')
        type_ = count.keys()
        type_count = ['count_blank', 'count_code', 'count_pound']
        self.assertEqual(type_, type_count)

    def test_count_php_line(self):
        count = Detection.count_php_line('./examples/cloc.php')
        type_ = count.keys()
        type_count = ['count_blank', 'count_code', 'count_pound']
        self.assertEqual(type_, type_count)

    def test_count_java_line(self):
        count = Detection.count_java_line('./examples/cloc.java')
        type_ = count.keys()
        type_count = ['count_blank', 'count_code', 'count_pound']
        self.assertEqual(type_, type_count)

    def test_count_html_line(self):
        count = Detection.count_html_line('./examples/cloc.html')
        type_ = count.keys()
        type_count = ['count_blank', 'count_code', 'count_pound']
        self.assertEqual(type_, type_count)

    def test_count_data_line(self):
        count = Detection.count_data_line('./examples/param_xml.xml')
        type_ = count.keys()
        type_count = ['count_blank', 'count_code', 'count_pound']
        self.assertEqual(type_, type_count)

    def test_countnum(self):
        count = {'count_blank': 10, 'count_code': 20, 'count_pound': 30}
        type_num = {'php': {'blank': 10, 'code': 10, 'pound': 10, 'files': 2}}
        ext = 'php'
        type_num = Detection.countnum(count, type_num, ext)
        self.assertTrue(type_num.has_key('php'))

    def test_count_total_num(self):
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
        self.assertIsInstance(total_file, int)
        self.assertIsInstance(total_blank_line, int)
        self.assertIsInstance(total_pound_line, int)
        self.assertIsInstance(total_code_line, int)

    def test_cloc(self):
        self.assertTrue(Detection('./examples', '.').cloc())
