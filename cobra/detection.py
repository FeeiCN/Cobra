# -*- coding: utf-8 -*-

"""
    detection
    ~~~~~~~~~

    Implements detection language/framework

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
from prettytable import PrettyTable
import xml.etree.ElementTree as eT
from .rule import Rule
from log import logger
from pip.req import parse_requirements

file_type = []


class Detection(object):
    def __init__(self, target_directory, files):
        """

        :param target_directory:
        :param files:
        """
        self.target_directory = target_directory
        self.directory = os.path.abspath(self.target_directory)
        self.files = files
        self.lang = None
        self.requirements = None
        self.frame_data = {}
        self.language_data = {}
        self.project_data = []

    @property
    def language(self):
        """Detection main language"""
        languages = Rule().languages
        tmp_language = None
        for ext, ext_info in self.files:
            logger.debug("{ext} {count}".format(ext=ext, count=ext_info['count']))
            for language, language_info in languages.items():
                if ext in language_info['extensions']:
                    if 'chiefly' in language_info and language_info['chiefly'].lower() == 'true':
                        logger.debug('found the chiefly language({language}), maybe have largest, continue...'.format(
                            language=language))
                        self.lang = language
                    else:
                        logger.debug('not chiefly, continue...'.format(language=language))
                        tmp_language = language
            if self.lang is None:
                logger.debug('not found chiefly language, use the largest language(language) replace'.format(
                    language=tmp_language))
                self.lang = tmp_language
        logger.debug('main language({main_language}), tmp language({tmp_language})'.format(tmp_language=tmp_language,
                                                                                           main_language=self.lang))
        return self.lang

    def framework(self):
        tree = self.rule()
        root = tree.getroot()
        frame_data, language_data = self.parse_xml(root, self.frame_data, self.language_data)
        projects_data = self.project_information(self.target_directory, False)
        frames_name = frame_data.keys()
        for frame_name in frames_name:
            for rule_name in frame_data[frame_name]:
                for project_data in projects_data:
                    if rule_name in project_data:
                        result = logger.info("Find the project's framework may be:" + frame_name)
                        return result
        logger.info('Unknown Framework')
        return 'Unknown Framework'

    def _requirements(self):
        requirements_txt = os.path.join(self.directory, 'requirements.txt')
        logger.debug(requirements_txt)
        if os.path.isfile(requirements_txt):
            requirements = parse_requirements(requirements_txt, session=False)
            self.requirements = [req.name.strip().lower() for req in requirements]
            logger.debug('requirements modules count: {count} ({modules})'.format(count=len(self.requirements),
                                                                                  modules=','.join(self.requirements)))
        else:
            logger.debug('requirements.txt not found!')
            self.requirements = []

    def parse_xml(self, root, frame_data, language_data, frame_name=None):
        language_name = ''
        if len(root) != 0:
            try:
                frame_name = root.attrib['name']
                language_name = root.attrib['language']
                frame_data.setdefault(frame_name, [])
            except KeyError:
                logger.warning('This Element is the root')
            for child_of_root in root:
                frame_data, language_data = self.parse_xml(child_of_root, frame_data, language_data, frame_name)
                language_data.setdefault(language_name, {})
            try:
                language_data[language_name].setdefault(frame_name, frame_data[frame_name])
            except KeyError:
                logger.warning('This Element is the root')
            return frame_data, language_data
        else:
            try:
                frame_data[frame_name].append(root.attrib['value'])
                return frame_data, language_data
            except KeyError, e:
                logger.warning(e.message)

    @staticmethod
    def rule():
        project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        rules_path = os.path.join(project_directory, 'cobra/rules/frameworks.xml')
        tree = eT.ElementTree(file=rules_path)
        return tree

    @staticmethod
    def get_dict(extension, type_num):
        for ext in extension:
            type_num.setdefault(ext, {'files': 0, 'blank': 0, 'pound': 0, 'code': 0})
        return type_num

    @staticmethod
    def project_information(absolute_path, extension, is_cloc=False):
        allfiles = []
        if os.path.isdir(absolute_path):
            for root, dirs, filenames in os.walk(absolute_path):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    if is_cloc is True:
                        fileext = os.path.splitext(filepath)[1][1:]
                        if fileext in extension:
                            allfiles.append(filepath)
                    else:
                        allfiles.append(filepath)
        if os.path.isfile(absolute_path):
            absolute_path = os.path.abspath(absolute_path)
            if is_cloc is True:
                fileext = os.path.splitext(absolute_path)[1][1:]
                if fileext in extension:
                    allfiles.append(absolute_path)
            else:
                allfiles.append(absolute_path)
        return allfiles

    # 统计Python数据的函数
    @staticmethod
    def count_py_line(filename):
        count = {'count_code': 0, 'count_blank': 0, 'count_pound': 0}
        fi = open(filename, 'r')
        file_line = fi.readline()
        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.strip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('#'):
                count['count_pound'] += 1
            elif file_line.count('"""') == 2 or file_line.count("'''") == 2:
                if file_line.startswith('"""') or file_line.startswith("'''"):
                    count['count_pound'] += 1
                else:
                    count['count_code'] += 1
            elif file_line.count('"""') == 1 or file_line.count("'''") == 1:
                if file_line.startswith('"""') or file_line.startswith("'''"):
                    count['count_pound'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_pound'] += 1
                        if file_line.endswith('"""\n') or file_line.endswith("'''\n"):
                            break
                else:
                    count['count_code'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_code'] += 1
                        if file_line.find('"""') or file_line.find("'''"):
                            break
            else:
                count['count_code'] += 1
            file_line = fi.readline()
        fi.close()
        return count

    # 统计PHP数据的函数
    @staticmethod
    def count_php_line(filename):
        count = {'count_code': 0, 'count_blank': 0, 'count_pound': 0}
        fi = open(filename, 'r')
        file_line = fi.readline()
        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('//') or file_line.startswith('#'):
                count['count_pound'] += 1
            elif file_line.count('/*') == 1 and file_line.count('*/') == 1:
                if file_line.startswith('/*'):
                    count['count_pound'] += 1
                else:
                    count['count_code'] += 1
            elif file_line.count('/*') == 1 and file_line.count('*/') == 0:
                if file_line.startswith('/*'):
                    count['count_pound'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_pound'] += 1
                        if file_line.endswith('*/\n'):
                            break
                else:
                    count['count_code'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_code'] += 1
                        if file_line.find('*/'):
                            break
            else:
                count['count_code'] += 1
            file_line = fi.readline()
        fi.close()
        return count

    # 统计Java和JS数据的函数
    @staticmethod
    def count_java_line(filename):
        count = {'count_code': 0, 'count_blank': 0, 'count_pound': 0}
        fi = open(filename, 'r')
        file_line = fi.readline()
        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('//'):
                count['count_pound'] += 1
            elif file_line.count('/*') == 1 and file_line.count('*/') == 1:
                if file_line.startswith('/*'):
                    count['count_pound'] += 1
                else:
                    count['count_code'] += 1
            elif file_line.count('/*') == 1 and file_line.count('*/') == 0:
                if file_line.startswith('/*'):
                    count['count_pound'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_pound'] += 1
                        if file_line.endswith('*/\n'):
                            break
                else:
                    count['count_code'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_code'] += 1
                        if file_line.find('*/'):
                            break
            else:
                count['count_code'] += 1
            file_line = fi.readline()
        fi.close()
        return count

    # 统计HTML,CSS数据的函数
    @staticmethod
    def count_html_line(filename):
        count = {'count_code': 0, 'count_blank': 0, 'count_pound': 0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.count('<!--') == 1 and file_line.count('-->') == 1:
                if file_line.startswith('<!--'):
                    count['count_pound'] += 1
                else:
                    count['count_code'] += 1
            elif file_line.count('<!--') == 1 and file_line.count('-->') == 0:
                if file_line.startswith('<!--'):
                    count['count_pound'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_pound'] += 1
                        if file_line.endswith('-->\n'):
                            break
                else:
                    count['count_code'] += 1
                    while True:
                        file_line = fi.readline()
                        if len(file_line) == 0 or file_line == "\n":
                            count['count_blank'] += 1
                        else:
                            count['count_code'] += 1
                        if file_line.find('-->'):
                            break
            else:
                count['count_code'] += 1
            file_line = fi.readline()
        fi.close()
        return count

    # 统计markdown和xml数据的函数
    @staticmethod
    def count_data_line(filename):
        count = {'count_code': 0, 'count_blank': 0, 'count_pound': 0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            else:
                count['count_code'] += 1
            file_line = fi.readline()
        fi.close()
        return count

    @staticmethod
    def countnum(count, type_num, fileext):
        type_num[fileext]['blank'] += count['count_blank']
        type_num[fileext]['code'] += count['count_code']
        type_num[fileext]['pound'] += count['count_pound']
        type_num[fileext]['files'] += 1
        return type_num

    @staticmethod
    def count_total_num(type_num, extension, total_file, total_blank_line, total_pound_line, total_code_line):
        for lang in extension:
            total_file += type_num[lang]['files']
            total_blank_line += type_num[lang]['blank']
            total_pound_line += type_num[lang]['pound']
            total_code_line += type_num[lang]['code']
        return total_file, total_blank_line, total_pound_line, total_code_line

    """
    type_num = {'js':{'files':0, 'blank':0, 'pound':0, 'code':0}, 
                'php':{'files':0, 'blank':0, 'pound':0, 'code':0}
                }
    For additional file types, you need to add a file suffix to the extension and add the file suffix to the if
    statement corresponding to the comment, example:

    if fileext == 'py' or fileext == 'java' or fileext == 'xxx'
    """

    def cloc(self):
        extension = ['js', 'py', 'php', 'java', 'xml', 'css', 'html', 'md', 'm']
        type_num = {}
        total_code_line = 0
        total_pound_line = 0
        total_blank_line = 0
        total_file = 0
        type_num = self.get_dict(extension, type_num)
        filelists = self.project_information(self.directory, extension, True)
        for filelist in filelists:
            try:
                fileext = os.path.splitext(filelist)[1][1:]
                if fileext not in file_type:
                    file_type.append(fileext)
                if fileext == 'py':
                    count = self.count_py_line(filelist)
                    type_num = self.countnum(count, type_num, fileext)
                if fileext == 'js' or fileext == 'java' or fileext == 'css' or fileext == 'm':
                    count = self.count_java_line(filelist)
                    type_num = self.countnum(count, type_num, fileext)
                if fileext == 'php':
                    count = self.count_php_line(filelist)
                    type_num = self.countnum(count, type_num, fileext)
                if fileext == 'md' or fileext == 'xml':
                    count = self.count_data_line(filelist)
                    type_num = self.countnum(count, type_num, fileext)
                if fileext == 'html':
                    count = self.count_html_line(filelist)
                    type_num = self.countnum(count, type_num, fileext)
            except:
                logger.info('Part of the annotation rule does not match, press CTRL + C to continue the program')
        total_file, total_blank_line, total_pound_line, total_code_line = self.count_total_num(type_num, extension,
                                                                                               total_file,
                                                                                               total_blank_line,
                                                                                               total_pound_line,
                                                                                               total_code_line)
        x = PrettyTable(["language", "files", "blank", "comment", "code"])
        x.padding_width = 2
        x.align = "l"
        for lang in file_type:
            try:
                x.add_row([lang, type_num[lang]['files'], type_num[lang]['blank'], type_num[lang]['pound'],
                           type_num[lang]['code']])
            except KeyError:
                logger.warning('There is no such file type -->'+lang + ',please add it to the whitelist')
        x.add_row(["SUM", total_file, total_blank_line, total_pound_line, total_code_line])
        logger.info('\n' + str(x))
        return True
