# -*- coding: utf-8 -*-
import unittest
import os
import xml.etree.ElementTree as eT
from cobra.dependencies import Dependencies


class TestDependencies(unittest.TestCase):
    def test_find_file(self):
        dependencies = Dependencies('./examples')
        file_path, flag = dependencies.find_file()
        self.assertIsInstance(file_path, str)
        self.assertIsInstance(flag, int)

    def test_get_path(self):
        dependencies = Dependencies('./examples')
        for root, dirs, filenames in os.walk(dependencies.directory):
            for filename in filenames:
                file_path = dependencies.get_path(root, filename)
                self.assertIsInstance(file_path, str)

    def test_find_python_pip(self):
        dependencies = Dependencies('./examples')
        dependencies.find_python_pip('./examples/requirements.txt')
        self.assertTrue('Flask' in dependencies.get_result)

    def test_find_java_mvn(self):
        dependencies = Dependencies('./examples')
        dependencies.find_java_mvn('./examples/pom.xml')
        self.assertTrue('org.commonjava.maven.ext/pom-manipulation-io' in dependencies.get_result)

    def test_find_oc_pods(self):
        dependencies = Dependencies('./examples')
        dependencies.find_oc_pods('./examples/profile')
        self.assertTrue('MJExtension' in dependencies.get_result)

    def test_pods_statistical(self):
        dependencies = Dependencies('./examples')
        info = [" 'Alamofire1'", " :path => '~/Documents/Alamofire'"]
        dependencies.pods_statistical(info)
        self.assertTrue('Alamofire1' in dependencies.get_result)

    def test_pods_version(self):
        dependencies = Dependencies('./examples/')
        info = ":branch => 'dev'"
        version = dependencies.pods_version(info)
        self.assertTrue('branch' in version)

    def test_remove_quotes(self):
        dependencies = Dependencies('./examples')
        info ="  'Alamofire1'"
        result = dependencies.remove_quotes(info)
        self.assertEqual('Alamofire1', result)

    def test_parse_xml(self):
        dependencies = Dependencies('./examples/pom.xml')
        root = dependencies.parse_xml('./examples/pom.xml')
        root_test = eT.parse('./examples/pom.xml')
        self.assertIsInstance(root, type(root_test))

    def test_get_version(self):
        dependencies = Dependencies('./examples/requirements.txt')
        dependencies.dependencies()
        version = dependencies.get_version('Flask')
        self.assertEqual(version, '0.10.1')

    def test_get_result(self):
        dependencies = Dependencies('./examples/requirements.txt')
        dependencies.dependencies()
        result = dependencies.get_result
        self.assertIsInstance(result, dict)
