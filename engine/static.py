#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
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
from engine import rules, scan
from utils import log
from datetime import datetime
from app import db, CobraResults, CobraRules


class Static:
    def __init__(self, language=None, extensions=None):
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

    def analyse(self, directory=None):
        if directory is None:
            print("Please set directory")
            sys.exit()
        log.info('Start code static analyse...')

        s = scan.Scan(directory)
        files = s.files()
        language_ext = {
            'php': ['.php', '.php3', '.php4', '.php5'],
            'jsp': ['.jsp'],
            'java': ['.java'],
            'html': ['.htm', '.html', '.phps', '.phtml'],
            'js': ['.js']
        }
        ext_language = {
            # Image
            '.jpg': 'image',
            '.png': 'image',
            '.bmp': 'image',
            '.gif': 'image',
            '.ico': 'image',
            '.cur': 'image',
            # Font
            '.eot': 'font',
            '.otf': 'font',
            '.svg': 'font',
            '.ttf': 'font',
            '.woff': 'font',
            # CSS
            '.css': 'css',
            '.less': 'css',
            '.scss': 'css',
            '.styl': 'css',
            # Media
            '.mp3': 'media',
            '.swf': 'media',
            # Execute
            '.exe': 'execute',
            '.sh': 'execute',
            '.dll': 'execute',
            '.so': 'execute',
            '.bat': 'execute',
            '.pl': 'execute',
            # Edit
            '.swp': 'tmp',
            # Cert
            '.crt': 'cert',
            # Text
            '.txt': 'text',
            '.csv': 'text',
            '.md': 'markdown',
            # Backup
            '.zip': 'backup',
            '.bak': 'backup',
            '.tar': 'backup',
            '.tar.gz': 'backup',
            '.db': 'backup',
            # Config
            '.xml': 'config',
            '.yml': 'config',
            '.spf': 'config',
            '.iml': 'config',
            '.manifest': 'config',
            # Source
            '.psd': 'source',
            '.as': 'source',
            # Log
            '.log': 'log',
            # Template
            '.template': 'template',
            '.tpl': 'template',
        }
        for ext in files:
            if ext in ext_language:
                continue
                print ext, files[ext]
            else:
                print ext

        rules = CobraRules.query.all()
        for rule in rules:
            print rule

        # grep name is ggrep on mac
        grep = '/bin/grep'
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
            srcdir = '/Volumes/Statics/Project/Company/mogujie/public/test/'
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
                        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                        params = [scan_id, rule_id, rr[0], code[0], str(code[1].strip()),
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                                  datetime.now().strftime('%Y-%m-%d %H:%M:%S')]
                        try:
                            print('In Insert')
                            results = CobraResults(scan_id, rule_id, rr[0], code[0], str(code[1].strip()), current_time,
                                                   current_time)
                            db.session.add(results)
                            db.session.commit()
                            print('Insert Results Success')
                        except:
                            print('Insert Results Failed')
                        print params
                    except Exception as e:
                        log.debug('Error parsing result: ' + str(e))

            else:
                print result
                log.info('Not Found')

        except Exception as e:
            log.debug('Error calling grep: ' + str(e))
