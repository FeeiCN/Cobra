# -*- coding: utf-8 -*-
import os
import xml.etree.ElementTree as eT


class Dependencies(object):
    def __init__(self, target_directory):
        """
        :param target_directory: The project's path
        """
        self.directory = os.path.abspath(target_directory)
        self._result = {}
        self.dependencies()

    def dependencies(self):
        file_path, flag = self.find_file()
        if flag == 1:
            self.find_python_pip(file_path)
        if flag == 2:
            self.find_java_mvn(file_path)
        if flag == 3:
            self.find_oc_pods(file_path)

    def find_file(self):
        """
        :return:flag:{1:'python', 2:'java', 3:'oc'}
        """
        if os.path.isdir(self.directory):
            for root, dirs, filenames in os.walk(self.directory):
                for filename in filenames:
                    if filename == 'requirements.txt':
                        file_path = self.get_path(root, filename)
                        flag = 1
                        return file_path, flag
                    if filename == 'pom.xml':
                        file_path = self.get_path(root, filename)
                        flag = 2
                        return file_path, flag
                    if filename == 'profile':
                        file_path = self.get_path(root, filename)
                        flag = 3
                        return file_path, flag
        else:
            file_path = os.path.basename(self.directory)
            if file_path == 'requirements.txt':
                flag = 1
                return self.directory, flag
            if file_path == 'pom.xml':
                flag = 2
                return self.directory, flag
            if file_path == 'profile':
                flag = 3
                return self.directory, flag

    @staticmethod
    def get_path(root, filename):
        """
        :param root:
        :param filename:
        :return:
        """
        return os.path.join(root, filename)

    def find_python_pip(self, file_path):
        with open(file_path) as fi:
            for line in fi.readlines():
                flag = line.index("==")
                module_ = line[:flag]
                version = line[flag+2:].strip()
                self._result[module_] = version

    def find_java_mvn(self, file_path):
        pom_ns = "{http://maven.apache.org/POM/4.0.0}"
        tree = self.parse_xml(file_path)
        root = tree.getroot()
        childs = root.iter('%sdependency' % pom_ns)
        for child in childs:
            group_id = child.getchildren()[0].text
            artifact_id = child.getchildren()[1].text
            version = child.getchildren()[2].text
            module_ = artifact_id
            self._result[module_] = version

    def find_oc_pods(self, file_path):
        with open(file_path) as fi:
            for line in fi.readlines():
                line = line.strip()
                if line.startswith('pod'):
                    info = line[3:].split(',')
                    self.pods_statistical(info)

    def pods_statistical(self, info):
        version = ""
        module_ = self.remove_quotes(info[0])
        if len(info) == 1:  # moule from pods, version is the latest version
            version = 'The latest version'
        if len(info) == 2:  # module from pods, version is old
            version = self.remove_quotes(info[1])
        if len(info) == 2 and info[1].find('path') != -1:  # module from local
            index = info[1].find('=>')
            version = self.remove_quotes(info[1][index+2:])
        if len(info) >= 2 and info[1].find('git') != -1:  # module from git
            if len(info) == 2:
                version = {'branch': 'master'}  # branch is master
            else:
                version = self.pods_version(info[2])  # branch is other or tag or commit version
        self._result[module_] = version

    def pods_version(self, info):
        """
        :param info:
        :return: dict example {'branch':'dev'} {'commit':'*******'} {'tag':'3.1.1'} from git information
        """
        version = {}
        tag = info.split('=>')
        version[tag[0].strip().lstrip(':')] = self.remove_quotes(tag[1])
        return version

    @staticmethod
    def remove_quotes(info):
        return info.strip().strip('"').strip("'")

    @staticmethod
    def parse_xml(file_path):
        return eT.parse(file_path)

    def get_version(self, module_):
        return self._result[module_]

    @property
    def get_result(self):
        return self._result
