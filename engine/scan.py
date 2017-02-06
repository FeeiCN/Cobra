#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    engine.scan
    ~~~~~~~~~~~

    Implements scan

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import time
import subprocess
import getpass
import logging
from app import db, CobraProjects, CobraTaskInfo
from utils import config, decompress, log
from pickup import git
from engine import detection

log.Log()
logging = logging.getLogger(__name__)


class Scan:
    def __init__(self, target):
        """
        Set target
        :param target: compress(filename) version(repository)
        """
        self.target = target.strip()

    def compress(self):
        dc = decompress.Decompress(self.target)
        ret, result_d = dc.decompress()
        if ret is False:
            return 1002, result_d
        else:
            directory = result_d
        logging.info("Scan directory: {0}".format(directory))
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())

        p = CobraProjects.query.filter_by(repository=directory).first()

        # detection framework for project
        framework, language = detection.Detection(directory).framework()
        if framework != '' or language != '':
            project_framework = '{0} ({1})'.format(framework, language)
        else:
            project_framework = ''
        if not p:
            # insert into project table.
            repo_name = directory.split('/')[-1]
            project = CobraProjects(directory, '', repo_name, 'Upload', project_framework, '', '', 1, current_time)
            db.session.add(project)
            db.session.commit()
            project_id = project.id
        else:
            project_id = p.id
            # update project's framework
            p.framework = project_framework
            db.session.add(p)

        task = CobraTaskInfo(directory, '', 3, '', '', 0, 0, 0, 1, 0, 0, current_time, current_time)
        db.session.add(task)
        db.session.commit()
        cobra_path = os.path.join(config.Config().project_directory, 'cobra.py')
        if os.path.isfile(cobra_path) is not True:
            return 1004, 'Cobra Not Found'
        # 扫描漏洞
        subprocess.Popen(['python', cobra_path, "scan", "-p", str(project_id), "-i", str(task.id), "-t", directory])
        # 统计代码行数
        subprocess.Popen(['python', cobra_path, "statistic", "-i", str(task.id), "-t", directory])
        # 检测漏洞修复状况
        subprocess.Popen(['python', cobra_path, "repair", "-p", str(project_id)])
        result = dict()
        result['scan_id'] = task.id
        result['project_id'] = project_id
        result['msg'] = u'success'
        return 1001, result

    def version(self, branch=None, new_version=None, old_version=None):
        # Gitlab
        if '.git' in self.target:
            logging.info('Gitlab project')
            # Git
            if 'gitlab' in self.target:
                username = config.Config('git', 'username').value
                password = config.Config('git', 'password').value
            else:
                username = None
                password = None
            gg = git.Git(self.target, branch=branch, username=username, password=password)
            repo_author = gg.repo_author
            repo_name = gg.repo_name
            repo_directory = gg.repo_directory
            # Git Clone Error
            clone_ret, clone_err = gg.clone()
            if clone_ret is False:
                return 4001, 'Clone Failed ({0})'.format(clone_err)
        elif 'svn' in self.target:
            # SVN
            repo_name = 'mogujie'
            repo_author = 'all'
            repo_directory = config.Config('upload', 'directory').value
        else:
            repo_name = 'Local Project'
            repo_author = getpass.getuser()
            repo_directory = self.target
            if not os.path.exists(repo_directory):
                return 1004, 'repo directory not exist ({0})'.format(repo_directory)

        if new_version == "" or old_version == "":
            scan_way = 1
        else:
            scan_way = 2
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        # insert into task info table.
        task = CobraTaskInfo(self.target, branch, scan_way, new_version, old_version, 0, 0, 0, 1, 0, 0, current_time, current_time)

        p = CobraProjects.query.filter_by(repository=self.target).first()
        project = None

        # detection framework for project
        framework, language = detection.Detection(repo_directory).framework()
        if framework != '' or language != '':
            project_framework = '{0} ({1})'.format(framework, language)
        else:
            project_framework = ''
        project_id = 0
        if not p:
            # insert into project table.
            project = CobraProjects(self.target, '', repo_name, repo_author, project_framework, '', '', 1, current_time)
        else:
            project_id = p.id
            # update project's framework
            p.framework = project_framework
            db.session.add(p)
        try:
            db.session.add(task)
            if not p:
                db.session.add(project)
            db.session.commit()
            if not p:
                project_id = project.id
            cobra_path = os.path.join(config.Config().project_directory, 'cobra.py')

            if os.path.isfile(cobra_path) is not True:
                return 1004, 'cobra.py not found'
            # scan vulnerability
            subprocess.Popen(['python', cobra_path, "scan", "-p", str(project_id), "-i", str(task.id), "-t", repo_directory])
            # statistic code
            subprocess.Popen(['python', cobra_path, "statistic", "-i", str(task.id), "-t", repo_directory])
            # check repair
            subprocess.Popen(['python', cobra_path, "repair", "-p", str(project_id)])
            result = dict()
            result['scan_id'] = task.id
            result['project_id'] = project_id
            result['msg'] = u'success'
            return 1001, result
        except Exception as e:
            return 1004, 'Unknown error, try again later?' + e.message
