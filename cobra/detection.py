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
import re
import os
from .rule import Rule
from log import logger
from pip.req import parse_requirements
from prettytable import PrettyTable
try:
    import xml.etree.cElementTree as ET
except ImportError:
    import xml.etree.ElementTree as ET

extension = ['js', 'py', 'php', 'java', 'xml', 'css', 'html', 'md', 'm']
file_type = []

class Detection(object):
    def __init__(self, target_directory, files):
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
                        logger.debug('found the chiefly language({language}), maybe have largest, continue...'.format(language=language))
                        self.lang = language
                    else:
                        logger.debug('not chiefly, continue...'.format(language=language))
                        tmp_language = language
            if self.lang is None:
                logger.debug('not found chiefly language, use the largest language(language) replace'.format(language=tmp_language))
                self.lang = tmp_language
        logger.debug('main language({main_language}), tmp language({tmp_language})'.format(tmp_language=tmp_language, main_language=self.lang))
        return self.lang

    @property
    def framework(self):
        tree = self.rule()
        root = tree.getroot()
        frame_data, language_data = self.parseXml(root, self.frame_data, self.language_data)
        projects_data = self.projectInformation(self.target_directory)
        frames_name = frame_data.keys()
        for frame_name in frames_name:
            for rule_name in frame_data[frame_name]:
                for project_data in projects_data:
                    if rule_name in project_data:
                        logger.info("Find the project's framework may be:" + frame_name)
                        return frame_name
        return 'Unknown Framework'

    def _requirements(self):
        requirements_txt = os.path.join(self.directory, 'requirements.txt')
        logger.debug(requirements_txt)
        if os.path.isfile(requirements_txt):
            requirements = parse_requirements(requirements_txt, session=False)
            self.requirements = [req.name.strip().lower() for req in requirements]
            logger.debug('requirements modules count: {count} ({modules})'.format(count=len(self.requirements), modules=','.join(self.requirements)))
        else:
            logger.debug('requirements.txt not found!')
            self.requirements = []

    def parseXml(self, root, frame_data, language_data):
        if len(root) != 0:
            try:
                global frame_name, language_name
                frame_name = root.attrib['name']
                language_name = root.attrib['language']
                frame_data.setdefault(frame_name, [])
            except KeyError, e:
                logger.warning(e.message)
            for child_of_root in root:
                frame_data, language_data = self.parseXml(child_of_root, frame_data, language_data)
            try:
                language_data.setdefault(language_name, {})
                language_data[language_name].setdefault(frame_name, frame_data[frame_name])
            except KeyError:
                logger.warning(e.message)
            return frame_data, language_data
        else:
            frame_data[frame_name].append(root.attrib['value'])
            return frame_data, language_data

    def projectInformation(self, absolute_path):
        allfiles = []
        if os.path.isdir(absolute_path):
            for root, dirs, filenames in os.walk(absolute_path):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    allfiles.append(filepath)
        if os.path.isfile(absolute_path):
            allfiles.append(absolute_path)
        return allfiles

    def rule(self):
        project_directory = os.path.abspath(os.path.join(os.path.dirname(__file__), os.pardir, os.pardir))
        rules_path = os.path.join(project_directory, 'cobra/rules/frameworks.xml')
        tree = ET.ElementTree(file=rules_path)
        return tree

    def getDict(self, extension, type_num):
        for ext in extension:
            type_num.setdefault(ext, {'files':0, 'blank':0, 'pound':0, 'code':0})
        return type_num

    def getFile(self, absolute_path, extension):
        allfiles = []
        if os.path.isdir(absolute_path):
            for root, dirs, filenames in os.walk(absolute_path):
                for filename in filenames:
                    filepath = os.path.join(root, filename)
                    fileext = os.path.splitext(filepath)[1][1:]
                    if fileext in extension:
                        allfiles.append(filepath)
        if os.path.isfile(absolute_path):
            allfiles.append(absolute_path)
        return allfiles

    #统计Python数据的函数
    def countPyLine(self, filename):
        count = {'count_code':0, 'count_blank':0, 'count_pound':0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('#'):
                count['count_pound'] += 1
            elif re.match('.*[\'|\(]""".+', file_line):
                count['count_code'] += 1
                while True:
                    file_line = fi.readline()
                    if len(file_line) == 0 or file_line == "\n":
                        count['count_blank'] += 1
                    else:
                        count['count_code'] += 1
                    if '"""' in file_line:
                        break
            elif re.match('^""".*"""$', file_line):
                count['count_pound'] += 1
            elif file_line.startswith('"""'):
                count['count_pound'] += 1
                while True:
                    file_line = fi.readline()
                    if len(file_line) == 0 or file_line == "\n":
                        count['count_blank'] += 1
                    else:
                        count['count_pound'] += 1
                    if file_line.endswith('"""\n'):
                        break
            else:
                count['count_code']  += 1
            file_line = fi.readline()
        return count

    #统计PHP数据的函数
    def countPHPLine(self, filename):
        count = {'count_code':0, 'count_blank':0, 'count_pound':0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('//') or file_line.startswith('#'):
                count['count_pound'] += 1
            elif re.match('.*[(\'"]/\*', file_line):
                count['count_code'] += 1
                while True:
                    file_line = fi.readline()
                    if len(file_line) == 0 or file_line == "\n":
                        count['count_blank'] += 1
                    else:
                        count['count_code'] += 1
                    if '*/' in file_line:
                        break
            elif re.match('^/\*.+\*/', file_line):
                count['count_pound'] += 1
            elif file_line.startswith('/*'):
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
                count['count_code']  += 1
            file_line = fi.readline()
        return count

    #统计Java和JS数据的函数
    def countJLine(self, filename):
        count = {'count_code':0, 'count_blank':0, 'count_pound':0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif file_line.startswith('//'):
                count['count_pound'] += 1
            elif re.match('.*[(\'"]/\*', file_line):
                count['count_code'] += 1
                while True:
                    file_line = fi.readline()
                    if len(file_line) == 0 or file_line == "\n":
                        count['count_blank'] += 1
                    else:
                        count['count_code'] += 1
                    if '*/' in file_line:
                        break
            elif re.match('^/\*.+\*/', file_line):
                count['count_pound'] += 1
            elif file_line.startswith('/*'):
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
                count['count_code']  += 1
            file_line = fi.readline()
        return count

    #统计HTML,CSS数据的函数
    def countHtmlLine(self, filename):
        count = {'count_code':0, 'count_blank':0, 'count_pound':0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            elif re.match('^<!--.+-->', file_line):
                count['count_pound'] += 1
            elif file_line.startswith('<!--'):
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
                count['count_code']  += 1
            file_line = fi.readline()
        return count

    #统计markdown和xml数据的函数
    def countDataLine(self, filename):
        count = {'count_code':0, 'count_blank':0, 'count_pound':0}
        fi = open(filename, 'r')
        file_line = fi.readline()

        while fi.tell() != os.path.getsize(filename):
            file_line = file_line.lstrip()
            if len(file_line) == 0:
                count['count_blank'] += 1
            else:
                count['count_code']  += 1
            file_line = fi.readline()
        return count

    def countNum(self, count, type_num, fileext):
        type_num[fileext]['blank'] += count['count_blank']
        type_num[fileext]['code'] += count['count_code']
        type_num[fileext]['pound'] += count['count_pound']
        type_num[fileext]['files'] += 1
        return type_num

    def countTotalNum(self, type_num, totalFile, totalBlankLine, totalPoundLine, totalCodeLine):
        for lang in extension:
            totalFile += type_num[lang]['files']
            totalBlankLine += type_num[lang]['blank']
            totalPoundLine += type_num[lang]['pound']
            totalCodeLine += type_num[lang]['code']
        return totalFile, totalBlankLine, totalPoundLine, totalCodeLine

    #统计数据 type_num = {'js':{'files':0, 'blank':0, 'pound':0, 'code':0}, 'php':{'files':0, 'blank':0, 'pound':0, 'code':0}}
    def cloc(self):
        type_num = {}
        totalCodeLine = 0
        totalPoundLine = 0
        totalBlankLine = 0
        totalFile = 0
        type_num = self.getDict(extension, type_num)
        filelists = self.getFile(self.directory, extension)
        for filelist in filelists:
            try:
                fileext = os.path.splitext(filelist)[1][1:]
                if fileext not in file_type:
                    file_type.append(fileext)
                if fileext == 'py':
                    count = self.countPyLine(filelist)
                    type_num = self.countNum(count, type_num, fileext)
                if fileext == 'js' or fileext == 'java' or fileext == 'css' or fileext == 'm':
                    count = self.countJLine(filelist)
                    type_num = self.countNum(count, type_num, fileext)
                if fileext == 'php':
                    count = self.countPHPLine(filelist)
                    type_num = self.countNum(count, type_num, fileext)
                if fileext == 'md' or fileext == 'xml':
                    count = self.countDataLine(filelist)
                    type_num = self.countNum(count, type_num, fileext)
                if fileext == 'html':
                    count = self.countHtmlLine(filelist)
                    type_num = self.countNum(count, type_num, fileext)
            except:
                logger.info('Part of the annotation rule does not match, press CTRL + C to continue the program')
        totalFile, totalBlankLine, totalPoundLine, totalCodeLine = self.countTotalNum(type_num ,totalFile, totalBlankLine, totalPoundLine, totalCodeLine)
        x = PrettyTable(["language", "files", "blank", "pound", "code"])
        x.padding_width = 2
        x.align = "l"
        for lang in file_type:
            x.add_row([lang, type_num[lang]['files'], type_num[lang]['blank'], type_num[lang]['pound'], type_num[lang]['code']])
        x.add_row(["SUM", totalFile, totalBlankLine, totalPoundLine, totalCodeLine])
        logger.info('\n'+str(x))