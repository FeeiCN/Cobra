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
import json
import os
import re
import xml.etree.cElementTree as eT
from distutils.version import LooseVersion

try:  # for pip >= 10
    from pip._internal.req import parse_requirements
except ImportError:  # for pip <= 9.0.3
    from pip.req import parse_requirements

try:
    from xml.etree.cElementTree import ParseError
except ImportError:
    from xml.parsers.expat import ExpatError

from .log import logger


class Version(LooseVersion):
    """
    处理 version 中的一些特殊情况
    """

    def __init__(self, vstring=None):
        self.vstring = vstring
        self.version = []
        LooseVersion.__init__(self, vstring=vstring)

    def parse(self, vstring):
        """
        version 字符串处理为列表
        1.2.x 处理为 1.2.0
        * 处理为 0
        :param vstring:
        :return:
        """
        components = [x for x in self.component_re.split(vstring)
                      if x and x != '.']
        for i, obj in enumerate(components):
            try:
                if obj == 'x' or obj == '*':
                    components[i] = 0
                else:
                    components[i] = int(obj)
            except ValueError:
                pass

        self.version = components


class Comparator:
    """
    只比较版本号部分，返回 True 为命中规则，False 为未命中
    """

    def __init__(self, rule_version, dep_version, fmt='python'):
        """
        初始化
        :param rule_version: 规则内的版本号
        :param dep_version: 依赖文件内的版本号
        :param fmt: 版本号的格式 支持 python nodejs java
        """
        # 版本号区间的分隔符
        self.types = {
            'python': ',',
            'nodejs': '||',
            'java': ',',
        }
        self.rule_version = rule_version.strip()
        self.dep_version = dep_version.strip()
        self.fmt = fmt if fmt in self.types else 'python'

    def parse_version(self, version_str, fmt='python'):
        """
        处理 version 字符串中的比较符号，如 >= > <= < ^ ~ * - 等
        :param version_str: version 字符串
        :param fmt: 格式
        :return: [(operator, version)]
        """
        splitter = self.types.get(fmt) if self.types.get(fmt) else ','

        if 'http' in version_str or 'file' in version_str or 'git' in version_str:
            # 引用外部地址的全部报为 0 版本
            return [('>=', Version('0.0.0'))]
        elif version_str == 'latest' or version_str == '*' or version_str == '':
            # 安装时为当时的最新版本，需要再次确认
            return [('>=', Version('0.0.0'))]
        elif splitter in version_str:
            # 不以数字开头，但有多个并列的关系需要处理
            versions = []
            for ver in version_str.split(splitter):
                if ' ' in ver.strip():
                    versions += ver.strip().split(' ')
                else:
                    versions.append(ver.strip())

            parsed = []
            for v in versions:
                parsed.append(self.simple_parse(v))
            return parsed
        elif ' ' in version_str:
            version_str = version_str.strip()
            if ' ' in version_str and splitter == '||':
                versions = []
                for ver in version_str.split(' '):
                    versions.append(ver.strip())
                parsed = []
                for v in versions:
                    parsed.append(self.simple_parse(v))
                return parsed
            else:
                version_str = version_str.replace(' ', '')
                return [self.simple_parse(version_str)]
        else:
            # 不以数字开头，匹配开头的运算符，之后的为版本号
            return [self.simple_parse(version_str)]

    @staticmethod
    def simple_parse(simple_version_str):
        """
        只处理形如 >=1.2.3 和 1.2.3 的
        :param simple_version_str: 需要处理的版本号字符串
        :return: (operator, version)
        """
        operator_re = re.compile(r'^(>|<|>=|<=|==|\^|~+?)\d')
        # 先去掉两边的空格
        simple_version_str = simple_version_str.strip()
        match = operator_re.match(simple_version_str)
        if match:
            operator = match.group(1)
            version = simple_version_str.replace(operator, '')
            return operator, Version(version)
        elif simple_version_str[0].isdigit():
            # 没匹配出运算符
            return '==', Version(simple_version_str)
        else:
            # 开头不是数字，位置运算符
            raise Exception('Unknown operator {}'.format(simple_version_str))

    def compare(self):
        """

        :return:
        """
        max_rule_version = max(self.parse_version(self.rule_version), key=lambda v: v[1])
        min_dep_version = min(self.parse_version(self.dep_version, fmt=self.fmt), key=lambda v: v[1])

        if min_dep_version[1] <= max_rule_version[1] and max_rule_version[0] != '==':
            # 依赖中的最小版本号比规则中的版本号小
            return True
        elif min_dep_version[1] == max_rule_version[1] and max_rule_version[0] == '==':
            return True
        elif min_dep_version[0] in ('<', '<='):
            # 最小依赖版本号比规则版本号大，但运算符是小于，应该没人这么干。。
            return True
        else:
            return False


class Dependencies(object):
    def __init__(self, target_directory):
        """
        :param target_directory: The project's path
        """
        self.directory = os.path.abspath(target_directory)
        # _result  {'flask': {'version': '==0.10.1', 'format': 'python'}, ...}
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
        if flag == 3:
            self.find_nodejs_npm(file_path)
            return True

    def find_file(self):
        """
        :return:flag:{1:'python', 2:'java', 3:'node.js'}
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
                    if filename == 'package.json':
                        file_path.append(self.get_path(root, filename))
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
            if filename == 'package.json':
                flag = 3
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
            if 'requirements.txt' in requirement:
                reqs = parse_requirements(filename=requirement, session=False)
                for r in reqs:
                    module_ = r.name
                    version_ = r.specifier
                    self._framework.append(module_)
                    self._result.update(
                        {
                            module_: {
                                'version': str(version_),
                                'format': 'python',
                            }
                        }
                    )
            elif 'package.json' in requirement:
                self.find_nodejs_npm([requirement])

    def find_java_mvn(self, file_path):
        pom_ns = "{http://maven.apache.org/POM/4.0.0}"
        properties = {}

        for pom in file_path:
            if 'pom.xml' in pom:
                try:
                    tree = self.parse_xml(pom)
                    root = tree.getroot()
                    childs = root.findall('.//%sdependency' % pom_ns)
                    for child in childs:
                        group_id = child.getchildren()[0].text
                        artifact_id = child.getchildren()[1].text
                        if len(child.getchildren()) > 2:
                            version = child.getchildren()[2].text
                            version_match = re.match(r'\${(.*)}', version)
                            if version_match:
                                version_var = version_match.group(1)
                                ver_num = root.findall('.//{pom}{ver}'.format(pom=pom_ns, ver=version_var))
                                if ver_num:
                                    version = ver_num[0].text
                                    properties.update({
                                        version_var: version
                                    })
                                elif version_var in properties:
                                    version = properties.get(version_var)
                                else:
                                    version = '0.0.0'
                        else:
                            # 不确定版本，需要自查
                            version = '0.0.0'
                        module_ = artifact_id
                        self._framework.append(group_id)
                        self._framework.append(artifact_id)
                        self._result.update(
                            {
                                module_: {
                                    'version': str(version),
                                    'format': 'java',
                                }
                            }
                        )
                except ParseError:
                    logger.warning('[DEP] The {} have invalid token'.format(pom))
            elif 'package.json' in pom:
                self.find_nodejs_npm([pom])

    def find_nodejs_npm(self, file_path):
        """
        处理 package.json 依赖
        :param file_path: 接收文件名 list
        :return:
        """
        for npm in file_path:
            if 'package.json' in npm:
                with open(npm, 'r') as fi:
                    try:
                        package = json.load(fi)
                        deps = package.get('dependencies')
                        if deps:
                            for dep in deps:
                                module_ = dep
                                version = deps.get(dep)
                                self._framework.append(module_)
                                self._result.update({
                                    module_: {
                                        'version': str(version),
                                        'format': 'nodejs',
                                    }
                                })
                        else:
                            logger.info('[DEP] {} has no dependencies'.format(npm))
                    except json.JSONDecodeError:
                        logger.warning('[DEP] {} is not a valid json file'.format(npm))

    @staticmethod
    def parse_xml(file_path):
        return eT.parse(file_path)

    def get_version(self, module_):
        return self._result[module_].get('version')

    @property
    def get_result(self):
        return self._result

    @property
    def get_framework(self):
        return self._framework
