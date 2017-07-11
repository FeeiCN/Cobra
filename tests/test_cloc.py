# -*- coding: utf-8 -*-
import os
import re
import time
from prettytable import PrettyTable

absolute_path = "."
#absolute_path = sys.argv[1]
extension = ['js', 'py', 'php', 'java','xml', 'css', 'html', 'md']
aaa = dict.fromkeys(extension, {'files', 'blank', 'pound', 'code'})


def getFile(absolute_path, extension = ['js', 'py', 'php', 'java', 'xml', 'css', 'html', 'md']):
    allfiles = []
    for root, dirs, filenames in os.walk(absolute_path):
        for filename in filenames:
            filepath = os.path.join(root, filename)
            fileext = os.path.splitext(filepath)[1][1:]
            if fileext in extension:
                allfiles.append(filepath)
    return allfiles

def countLine(filename):
    count = {'count_code':0, 'count_block':0, 'count_pound':0}
    fi = open(filename, 'r')
    file_line = fi.readline()

    while fi.tell() != os.path.getsize(filename):
        file_line.strip()
        #if file_line == '\n' or file_line == '\t\n':
        if re.match('\s', file_line) and len(file_line) != 0:
            count['count_block'] += 1
        elif file_line.startswith('#') or file_line.startswith('@') or file_line.startswith('//'):
            count['count_pound'] += 1
        elif file_line.startswith('"""'):
            count['count_pound'] += 1
            while True:
                file_line = fi.readline()
                count['count_pound'] += 1
                if file_line.endswith('"""\n'):
                    break
        else:
            count['count_code']  += 1
        file_line = fi.readline()
    print '\n'
    print filename + '\t----codeLine----\t', count['count_code']
    print filename + '\t----blockLine----\t', count['count_block']
    print filename + '\t----poundLine----\t', count['count_pound']
    return count


if __name__ == "__main__":
    startTime = time.clock()
    filelists = getFile(absolute_path)
    totalCodeLine = 0
    totalPoundLine = 0
    totalBlockLine = 0
    totalFile = 0
    for filelist in filelists:
        #totalline = totalline + countLine(filelist)['count_code']
        totalFile += 1
        count = countLine(filelist)
        totalCodeLine += count['count_code']
        totalBlockLine += count['count_block']
        totalPoundLine += count['count_pound']
    # print '****************'
    # print 'The code of totalline:', totalCodeLine
    # print 'The block of totalline', totalBlockLine
    # print 'The pound of totalline', totalPoundLine
    # print 'The files of totalfile', totalFile
    # print "language\tfiles\tblank\tpound\tcode"
    # for i in extension:
    #     print i + "\t\t\t\t"
    # print "SUM:\t",totalFile, "\t", totalBlockLine, "\t", totalPoundLine , "\t" ,totalCodeLine
    x = PrettyTable(["language", "files", "blank", "pound", "code"])
    x.padding_width = 2
    x.align = "l"
    for lang in extension:
        x.add_row([lang, 0, 0, 0, 0])
    x.add_row(["SUM", totalFile, totalBlockLine, totalPoundLine, totalCodeLine])
    print x
