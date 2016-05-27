#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import os
import sys
import re
import subprocess
from engine import rules
from utils import log
from datetime import datetime


class Static:
    def __init__(self, language, extensions):
        self.language = language
        self.extensions = extensions

    def re_multi(self, file_paths):
        if self.language == 'php':
            patterns = rules.php_function()

        for file_path in file_paths:
            self.re_one(file_path, patterns)

    def re_one(self, file_path, pattern):
        # open the files
        input_file = open(file_path, 'r')

        # read the corpus first
        corpus_lines = input_file.readlines()

        # loop through each line in corpus
        for line_i in range(len(corpus_lines)):
            line = corpus_lines[line_i]

            # check if we have a regex match with "phrase" variable
            # if so, write it the output file
            if re.match(pattern, line):
                print(str(line_i + 1) + "\n")
        input_file.close()

    def analyse(self):
        log.info('Start code static analyse...')
        # grep name is ggrep on mac
        grep = 'grep'
        if 'darwin' == sys.platform:
            log.info('In Mac OS X System')
            for root, dirnames, filenames in os.walk('/usr/local/Cellar/grep'):
                for filename in filenames:
                    if 'ggrep' == filename:
                        grep = os.path.join(root, filename)

        filters = []
        for ext in self.extensions:
            filters.append('--include=*.' + ext)

        print filters
        log.info('Filter ')

        greps = 'eval\\s?\\('

        try:
            log.info('Scan Rule ID: 1')
            srcdir = '/Volumes/Statics/Project/Company/mogujie/appbeta/classes/controller'
            proc = subprocess.Popen([grep, "-n", "-r", "-P"] + filters + [greps, srcdir],
                                    stdout=subprocess.PIPE)
            result = proc.communicate()

            # Exists result
            if len(result[0]):
                log.info('Found:')
                perline = str(result[0]).split("\n")
                print perline
                for r in range(0, len(perline) - 1):
                    try:
                        basedir = '/Volumes/Statics/Project/Company/mogujie/'
                        rr = str(perline[r]).replace(basedir, '').split(':', 1)
                        code = str(rr[1]).split(':', 1)
                        scan_id = 1
                        rule_id = 1
                        params = [scan_id, rule_id, rr[0], code[0], str(code[1].strip()),
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        print params
                    except Exception as e:
                        log.debug('Error parsing result: ' + str(e))

            else:
                print result
                log.info('Not Found')

        except Exception as e:
            log.debug('Error calling grep: ' + str(e))
