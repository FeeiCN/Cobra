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
import time
import subprocess
import traceback
import logging
from engine.core import Core
from pickup import directory
from app import db, CobraRules, CobraLanguages, CobraTaskInfo, CobraWhiteList, CobraProjects, CobraVuls

logging = logging.getLogger(__name__)


class Static:
    def __init__(self, directory_path=None, task_id=None, project_id=None):
        self.directory = directory_path
        self.task_id = task_id
        self.project_id = project_id
        # project info
        project_info = CobraProjects.query.filter_by(id=project_id).first()
        if project_info:
            self.project_name = project_info.name
        else:
            self.project_name = 'Undefined Project'

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

        """
        all vulnerabilities
        vulnerabilities_all[vuln_id] = {'name': 'vuln_name', 'third_v_id': 'third_v_id'}
        """
        vulnerabilities_all = {}
        vulnerabilities = CobraVuls.query.all()
        for v in vulnerabilities:
            vulnerabilities_all[v.id] = {
                'name': v.name,
                'third_v_id': v.third_v_id
            }

        for rule in rules:
            rule.regex_location = rule.regex_location.strip()
            rule.regex_repair = rule.regex_repair.strip()
            logging.info('------------------\r\nScan rule id: {0} {1} {2}'.format(self.project_id, rule.id, rule.description))
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
                if rule.regex_location == "":
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

                logging.debug(' '.join(param))
                p = subprocess.Popen(param, stdout=subprocess.PIPE)
                result = p.communicate()

                # Exists result
                if len(result[0]):
                    lines = str(result[0]).strip().split("\n")
                    for line in lines:
                        line = line.strip()
                        if line == '':
                            continue
                        # 处理grep结果
                        if ':' in line:
                            line_split = line.split(':', 1)
                            file_path = line_split[0].strip()
                            code_content = line_split[1].split(':', 1)[1].strip()
                            line_number = line_split[1].split(':', 1)[0].strip()
                        else:
                            # 搜索文件
                            file_path = line
                            code_content = ''
                            line_number = 0
                        # 核心规则校验
                        result_info = {
                            'task_id': self.task_id,
                            'project_id': self.project_id,
                            'project_directory': self.directory,
                            'rule_id': rule.id,
                            'file_path': file_path,
                            'line_number': line_number,
                            'code_content': code_content,
                            'third_party_vulnerabilities_name': vulnerabilities_all[rule.vul_id]['name'],
                            'third_party_vulnerabilities_type': vulnerabilities_all[rule.vul_id]['third_v_id']
                        }
                        ret_status, ret_result = Core(result_info, rule, self.project_name, white_list).scan()
                        if ret_status is False:
                            logging.info("扫描 R: False {0}".format(ret_result))
                            continue

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
