#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    engine.scan
    ~~~~~~~~~~~

    Implements scan

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import time
import subprocess
import getpass
from app import db, CobraProjects, CobraTaskInfo
from utils import config, decompress, log
from pickup import git
from engine import detection


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
        log.info("Scan directory: {0}".format(directory))
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        task = CobraTaskInfo(self.target, '', 3, '', '', 0, 0, 0, 1, 0, 0, current_time, current_time)
        db.session.add(task)
        db.session.commit()
        cobra_path = os.path.join(config.Config().project_directory, 'cobra.py')
        if os.path.isfile(cobra_path) is not True:
            return 1004, 'Cobra Not Found'
        # Start Scanning
        subprocess.Popen(['python', cobra_path, "scan", "-p", str(0), "-i", str(task.id), "-t", directory])
        # Statistic Code
        subprocess.Popen(['python', cobra_path, "statistic", "-i", str(task.id), "-t", directory])
        result = dict()
        result['scan_id'] = task.id
        result['project_id'] = 0
        result['msg'] = u'success'
        return 1001, result

    def version(self, branch=None, new_version=None, old_version=None):
        # Gitlab
        if '.git' in self.target:
            # Git
            if 'gitlab' in self.target:
                username = config.Config('git', 'username').value
                password = config.Config('git', 'password').value
            else:
                username = False
                password = False
            gg = git.Git(self.target, branch=branch, username=username, password=password)
            repo_author = gg.repo_author
            repo_name = gg.repo_name
            repo_directory = gg.repo_directory
            # Git Clone Error
            if gg.clone() is False:
                return 4001, 'Clone Failed'
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
                return 1004, 'Repo_directory Not Found'

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
        project_framework = '{0} ({1})'.format(framework, language)
        if not p:
            # insert into project table.
            project = CobraProjects(self.target, '', repo_name, repo_author, project_framework, '', '', current_time)
            project_id = project.id
        else:
            project_id = p.id

            # update project's framework
            p.framework = project_framework
            db.session.add(p)
            db.session.commit()
        try:
            db.session.add(task)
            if not p:
                db.session.add(project)
            db.session.commit()

            cobra_path = os.path.join(config.Config().project_directory, 'cobra.py')

            if os.path.isfile(cobra_path) is not True:
                return 1004, 'Cobra Not Found'
            # Start Scanning
            subprocess.Popen(['python', cobra_path, "scan", "-p", str(project_id), "-i", str(task.id), "-t", repo_directory])
            # Statistic Code
            subprocess.Popen(['python', cobra_path, "statistic", "-i", str(task.id), "-t", repo_directory])
            result = dict()
            result['scan_id'] = task.id
            result['project_id'] = project_id
            result['msg'] = u'success'
            return 1001, result
        except Exception as e:
            return 1004, 'Unknown error, try again later?' + e.message
