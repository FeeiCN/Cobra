# -*- coding: utf-8 -*-
import os
import re
import sys
import time
from log import logger
from prettytable import PrettyTable

#absolute_path = "/Users/blbana/Croba/cobra/cobra/templates/asset"
absolute_path = sys.argv[1]
extension = ['js', 'py', 'php', 'java','xml', 'css', 'html', 'md']
type_num = {'js':{'files':0, 'blank':0, 'pound':0, 'code':0},'py':{'files':0, 'blank':0, 'pound':0, 'code':0},'php':{'files':0, 'blank':0, 'pound':0, 'code':0},
            'java':{'files':0, 'blank':0, 'pound':0, 'code':0},'xml':{'files':0, 'blank':0, 'pound':0, 'code':0},'css':{'files':0, 'blank':0, 'pound':0, 'code':0},
            'html':{'files':0, 'blank':0, 'pound':0, 'code':0},'md':{'files':0, 'blank':0, 'pound':0, 'code':0}}


def getFile(absolute_path, extension = ['js', 'py', 'php', 'java', 'xml', 'css', 'html', 'md']):
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
def countPyLine(filename):
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
def countPHPLine(filename):
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
def countJLine(filename):
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
def countHtmlLine(filename):
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
def countDataLine(filename):
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
    # print '\n'
    # print filename + '\t----codeLine----\t', count['count_code']
    # print filename + '\t----blankLine----\t', count['count_blank']
    # print filename + '\t----poundLine----\t', count['count_pound']
    return count

def countNum(count):
    type_num[fileext]['blank'] += count['count_blank']
    type_num[fileext]['code'] += count['count_code']
    type_num[fileext]['pound'] += count['count_pound']
    type_num[fileext]['files'] += 1
    return type_num

#统计数据 type_num = {'js':{'files':0, 'blank':0, 'pound':0, 'code':0}, 'php':{'files':0, 'blank':0, 'pound':0, 'code':0}}
if __name__ == "__main__":
    file_type = []
    startTime = time.clock()
    filelists = getFile(absolute_path)
    totalCodeLine = 0
    totalPoundLine = 0
    totalBlankLine = 0
    totalFile = 0
    for filelist in filelists:
        try:
            fileext = os.path.splitext(filelist)[1][1:]
            if fileext not in file_type:
                file_type.append(fileext)
            if fileext == 'py':
                count = countPyLine(filelist)
                type_num = countNum(count)
            if fileext == 'js' or fileext == 'java' or fileext == 'css':
                count = countJLine(filelist)
                type_num = countNum(count)
            if fileext == 'php':
                count = countPHPLine(filelist)
                type_num = countNum(count)
            if fileext == 'md' or fileext == 'xml':
                count = countDataLine(filelist)
                type_num = countNum(count)
            if fileext == 'html':
                count = countHtmlLine(filelist)
                type_num = countNum(count)
        except:
            logger.info('Part of the annotation rule does not match, press CTRL + C to continue the program')
    for lang in extension:
        totalFile += type_num[lang]['files']
        totalBlankLine += type_num[lang]['blank']
        totalPoundLine += type_num[lang]['pound']
        totalCodeLine += type_num[lang]['code']
    x = PrettyTable(["language", "files", "blank", "pound", "code"])
    x.padding_width = 2
    x.align = "l"
    for lang in file_type:
        x.add_row([lang, type_num[lang]['files'], type_num[lang]['blank'], type_num[lang]['pound'], type_num[lang]['code']])
    x.add_row(["SUM", totalFile, totalBlankLine, totalPoundLine, totalCodeLine])
    logger.info('\n'+str(x))
