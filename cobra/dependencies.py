# -*- coding: utf-8 -*-

"""
    dependencies
    ~~~~~~~~~~~~

    Implements Dependencies Check

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import xml.etree.cElementTree as eT
try:
    from xml.etree.cElementTree import ParseError
except ImportError:
    from xml.parsers.expat import ExpatError

from .log import logger


class Dependencies(object):
    def __init__(self, target_directory):
        """
        :param target_directory: The project's path
        """
        self.directory = os.path.abspath(target_directory)
        self._result = {}
        self._framework = []
        self.dependencies()

    def dependencies(self):
        file_path, flag = self.find_file()
        if flag == 0:  # flag == 0
            logger.debug('Dependency analysis cannot be done without finding dependency files')
            return False
        if flag == 1:
            self.find_python_pip(file_path)
            return True
        if flag == 2:
            self.find_java_mvn(file_path)
            return True

    def find_file(self):
        """
        :return:flag:{1:'python', 2:'java', 3:'oc'}
        """
        flag = 0
        file_path = []
        if os.path.isdir(self.directory):
            for root, dirs, filenames in os.walk(self.directory):
                for filename in filenames:
                    if filename == 'requirements.txt' and flag != 2:
                        file_path.append(self.get_path(root, filename))
                        flag = 1
                    if filename == 'pom.xml' and flag != 1:
                        file_path.append(self.get_path(root, filename))
                        flag = 2
            return file_path, flag
        else:
            filename = os.path.basename(self.directory)
            if filename == 'requirements.txt':
                flag = 1
                file_path.append(self.directory)
                return file_path, flag
            if filename == 'pom.xml':
                flag = 2
                file_path.append(self.directory)
                return file_path, flag
            return file_path, flag

    @staticmethod
    def get_path(root, filename):
        """
        :param root:
        :param filename:
        :return:
        """
        return os.path.join(root, filename)

    def find_python_pip(self, file_path):
        for requirement in file_path:
            with open(requirement) as fi:
                for line in fi.readlines():
                    flag = line.find("==")
                    if flag != -1:
                        module_ = line[:flag]
                        version = line[flag+2:].strip()
                        self._framework.append(module_)
                        self._result[module_] = version

    def find_java_mvn(self, file_path):
        pom_ns = "{http://maven.apache.org/POM/4.0.0}"
        for pom in file_path:
            try:
                tree = self.parse_xml(pom)
                root = tree.getroot()
                childs = root.findall('.//%sdependency' % pom_ns)
                for child in childs:
                    group_id = child.getchildren()[0].text
                    artifact_id = child.getchildren()[1].text
                    if len(child.getchildren()) > 2:
                        version = child.getchildren()[2].text
                    else:
                        version = 'The latest version'
                    module_ = artifact_id
                    self._framework.append(group_id)
                    self._framework.append(artifact_id)
                    self._result[module_] = version
            except ParseError:
                logger.warning('[DEP] The {} have invalid token'.format(pom))

    @staticmethod
    def parse_xml(file_path):
        return eT.parse(file_path)

    def get_version(self, module_):
        return self._result[module_]

    @property
    def get_result(self):
        return self._result

    @property
    def get_framework(self):
        return self._framework
