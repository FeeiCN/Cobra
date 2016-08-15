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
import time
import subprocess
from app import db, CobraProjects, CobraTaskInfo
from utils import config, decompress
from pickup import GitTools
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
        result = {}
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
            gg = GitTools.Git(self.target, branch=branch, username=username, password=password)
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
            repo_directory = os.path.join(config.Config('upload', 'directory').value, 'versions/mogujie/')
        else:
            return 1005, 'Repository must contained .git or svn'

        if new_version == "" or old_version == "":
            scan_way = 1
        else:
            scan_way = 2

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        # insert into task info table.
        task = CobraTaskInfo(self.target, branch, scan_way, new_version, old_version, 0, 0, 0, 1, 0, 0, current_time, current_time)

        p = CobraProjects.query.filter_by(repository=self.target).first()
        project = None
        if not p:
            # detection framework for project
            framework = detection.Detection(repo_directory).framework()
            # insert into project table.
            project = CobraProjects(self.target, '', repo_name, repo_author, framework, '', '', current_time)
            project_id = project.id
        else:
            project_id = p.id
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
            result = {}
            result['scan_id'] = task.id
            result['project_id'] = project_id
            result['msg'] = u'success'
            return 1001, result
        except Exception as e:
            return 1004, 'Unknown error, try again later?' + e.message
