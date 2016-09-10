#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    engine.static
    ~~~~~~~~~~~~~

    Implements static code analyse

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import sys
import re
import time
import subprocess
import traceback
import logging
from pickup import directory
from engine import parse
from app import db, CobraResults, CobraRules, CobraLanguages, CobraTaskInfo, CobraWhiteList

logging = logging.getLogger(__name__)


class Static:
    def __init__(self, directory_path=None, task_id=None, project_id=None):
        self.directory = directory_path
        self.task_id = task_id
        self.project_id = project_id

    def analyse(self):
        if self.directory is None:
            logging.critical("Please set directory")
            sys.exit()
        logging.info('Start code static analyse...')

        d = directory.Directory(self.directory)
        files = d.collect_files(self.task_id)
        logging.info('Scan Files: {0}, Total Time: {1}s'.format(files['file_nums'], files['collect_time']))

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
                logging.info('{0} - {1}'.format(ext, files[ext]))
                continue
            else:
                logging.info(ext)

        languages = CobraLanguages.query.all()

        rules = CobraRules.query.filter_by(status=1).all()
        extensions = None
        # `grep` (`ggrep` on Mac)
        grep = '/bin/grep'
        # `find` (`gfind` on Mac)
        find = '/bin/find'
        if 'darwin' == sys.platform:
            ggrep = ''
            gfind = ''
            for root, dir_names, file_names in os.walk('/usr/local/Cellar/grep'):
                for filename in file_names:
                    if 'ggrep' == filename or 'grep' == filename:
                        ggrep = os.path.join(root, filename)
            for root, dir_names, file_names in os.walk('/usr/local/Cellar/findutils'):
                for filename in file_names:
                    if 'gfind' == filename:
                        gfind = os.path.join(root, filename)
            if ggrep == '':
                logging.critical("brew install ggrep pleases!")
                sys.exit(0)
            else:
                grep = ggrep
            if gfind == '':
                logging.critical("brew install findutils pleases!")
                sys.exit(0)
            else:
                find = gfind

        for rule in rules:
            logging.info('Scan rule id: {0} {1} {2}'.format(self.project_id, rule.id, rule.description))
            # Filters
            for language in languages:
                if language.id == rule.language:
                    extensions = language.extensions.split('|')
            if extensions is None:
                logging.critical("Rule Language Error")
                sys.exit(0)

            # White list
            white_list = []
            ws = CobraWhiteList.query.filter_by(project_id=self.project_id, rule_id=rule.id, status=1).all()
            if ws is not None:
                for w in ws:
                    white_list.append(w.path)

            try:
                if rule.regex_location.strip() == "":
                    filters = []
                    for index, e in enumerate(extensions):
                        if index > 1:
                            filters.append('-o')
                        filters.append('-name')
                        filters.append('*' + e)
                    # Find Special Ext Files
                    param = [find, self.directory, "-type", "f"] + filters
                else:
                    filters = []
                    for e in extensions:
                        filters.append('--include=*' + e)

                    # explode dirs
                    explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
                    for explode_dir in explode_dirs:
                        filters.append('--exclude-dir={0}'.format(explode_dir))

                    # -n Show Line number / -r Recursive / -P Perl regular expression
                    param = [grep, "-n", "-r", "-P"] + filters + [rule.regex_location, self.directory]

                # logging.info(' '.join(param))
                p = subprocess.Popen(param, stdout=subprocess.PIPE)
                result = p.communicate()

                # Exists result
                if len(result[0]):
                    lines = str(result[0]).strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line == '':
                            continue
                        if rule.regex_location.strip() == '':
                            # Find
                            file_path = line.strip().replace(self.directory, '')
                            logging.debug('File: {0}'.format(file_path))
                            vul = CobraResults(self.task_id, rule.id, file_path, 0, '')
                            db.session.add(vul)
                        else:
                            # Grep
                            line_split = line.split(':', 1)
                            file_path = line_split[0].strip()
                            code_content = line_split[1].split(':', 1)[1].strip()
                            line_number = line_split[1].split(':', 1)[0].strip()

                            if file_path in white_list or ".min.js" in file_path:
                                logging.info("In white list or min.js")
                            else:
                                # annotation
                                # # // /* *
                                match_result = re.match("(#)?(//)?(\*)?(/\*)?", code_content)
                                if match_result.group(0) is not None and match_result.group(0) is not "":
                                    logging.info("In Annotation")
                                else:
                                    # parse file function structure
                                    if file_path[-3:] == 'php' and rule.regex_repair.strip() != '':
                                        try:
                                            parse_instance = parse.Parse(rule.regex_location, file_path, line_number, code_content)
                                            if parse_instance.is_controllable_param():
                                                if parse_instance.is_repair(rule.regex_repair, rule.block_repair):
                                                    logging.info("Static: repaired")
                                                    continue
                                                else:
                                                    found_vul = True
                                            else:
                                                logging.info("Static: uncontrollable param")
                                                continue
                                        except:
                                            print(traceback.print_exc())
                                            found_vul = False
                                    else:
                                        found_vul = True

                                    file_path = file_path.replace(self.directory, '')

                                    if found_vul:
                                        logging.info('In Insert')
                                        exist_result = CobraResults.query.filter_by(task_id=self.task_id, rule_id=rule.id, file=file_path, line=line_number).first()
                                        if exist_result is not None:
                                            logging.warning("Exists Result")
                                        else:
                                            logging.debug('File: {0}:{1} {2}'.format(file_path, line_number, code_content))
                                            vul = CobraResults(self.task_id, rule.id, file_path, line_number, code_content)
                                            db.session.add(vul)
                                            logging.info('Insert Results Success')
                    db.session.commit()
                else:
                    logging.info('Not Found')

            except Exception as e:
                print(traceback.print_exc())
                logging.critical('Error calling grep: ' + str(e))

        # Set End Time For Task
        t = CobraTaskInfo.query.filter_by(id=self.task_id).first()
        t.status = 2
        t.file_count = files['file_nums']
        t.time_end = int(time.time())
        t.time_consume = t.time_end - t.time_start
        t.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
        try:
            db.session.add(t)
            db.session.commit()
        except Exception as e:
            logging.critical("Set start time failed:" + e.message)
        logging.info("Scan Done")
