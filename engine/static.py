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
import time
import subprocess
from engine import rules, scan
from utils import log
from datetime import datetime
from app import db, CobraResults, CobraRules, CobraLanguages, CobraTaskInfo, CobraWhiteList


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
                log.debug(str(line_i + 1) + "\n")
        input_file.close()

    def analyse(self, directory=None, task_id=None, project_id=None):
        if directory is None:
            log.critical("Please set directory")
            sys.exit()
        log.info('Start code static analyse...')

        log.info('Parse target')

        s = scan.Scan(directory)
        files = s.files()
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
            '.rar': 'backup',
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
                log.info('{0} - {1}'.format(ext, files[ext]))
                continue
            else:
                log.info(ext)

        languages = CobraLanguages.query.all()

        rules = CobraRules.query.filter_by(status=1).all()
        extensions = None
        for rule in rules:
            for language in languages:
                if language.id == rule.language:
                    extensions = language.extensions.split('|')

            if extensions is None:
                log.warning("Rule Language Error")
            # grep name is ggrep on mac
            grep = '/bin/grep'
            if 'darwin' == sys.platform:
                log.info('In Mac OS X System')
                for root, dirnames, filenames in os.walk('/usr/local/Cellar/grep'):
                    for filename in filenames:
                        if 'ggrep' == filename:
                            grep = os.path.join(root, filename)

            filters = []
            for e in extensions:
                filters.append('--include=*' + e)

            # White list
            white_list = []
            ws = CobraWhiteList.query.filter_by(project_id=project_id, rule_id=rule.id, status=1).all()
            if ws is not None:
                for w in ws:
                    white_list.append(w.path)

            try:
                log.info('Scan rule id: {0}'.format(rule.id))
                # -n Show Line number / -r Recursive / -P Perl regular expression
                proc = subprocess.Popen([grep, "-n", "-r", "-P"] + filters + [rule.regex, directory],
                                        stdout=subprocess.PIPE)
                result = proc.communicate()

                # Exists result
                if len(result[0]):
                    log.info('Found:')
                    perline = str(result[0]).split("\n")
                    log.debug(perline)
                    for r in range(0, len(perline) - 1):
                        try:
                            rr = str(perline[r]).replace(directory, '').split(':', 1)
                            code = str(rr[1]).split(':', 1)
                            if task_id is None:
                                task_id = 0
                            rule_id = rule.id
                            current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
                            m_file = rr[0].strip()
                            m_line = code[0]
                            m_code = str(code[1].strip())
                            params = [task_id, rule_id, m_file, m_line, m_code, current_time,
                                      current_time]
                            try:
                                if m_file in white_list:
                                    log.debug("In White list")
                                else:
                                    # # // /* *
                                    match_result = re.match("(#)?(\/\/)?(\*)?(\/\*)?", m_code)
                                    if match_result.group(0) is not None and match_result.group(0) is not "":
                                        log.debug("In Annotation")
                                    else:
                                        log.debug('In Insert')
                                        if rule.regex == "":
                                            # Didn't filter line when regex is empty
                                            r_content = CobraResults.query.filter_by(task_id=task_id, rule_id=rule_id,
                                                                                     file=m_file).first()
                                            m_line = 0
                                        else:
                                            r_content = CobraResults.query.filter_by(task_id=task_id, rule_id=rule_id,
                                                                                     file=m_file,
                                                                                     line=m_line).first()
                                        if r_content is not None:
                                            log.warning("Exists Result")
                                        else:
                                            results = CobraResults(task_id, rule_id, m_file, m_line, m_code,
                                                                   current_time,
                                                                   current_time)
                                            db.session.add(results)
                                            db.session.commit()
                                            log.info('Insert Results Success')
                            except:
                                log.error('Insert Results Failed')
                            log.debug(params)
                        except Exception as e:
                            log.critical('Error parsing result: ' + str(e))

                else:
                    log.info('Not Found')

            except Exception as e:
                log.critical('Error calling grep: ' + str(e))

        # Set End Time For Task
        t = CobraTaskInfo.query.filter_by(id=task_id).first()
        t.status = 2
        t.file_count = files['file_nums']
        t.time_end = int(time.time())
        t.time_consume = t.time_end - t.time_start
        t.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
        try:
            db.session.add(t)
            db.session.commit()
        except Exception as e:
            log.critical("Set start time failed:" + e.message)

        log.info("Scan Done")
