#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.pull
    ~~~~~~~~

    Implements CLI pull

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import sys
import time
from flask_script import Command, Option
from app.models import CobraProjects
from app import db
from utils.log import logging
from engine import scan

logging = logging.getLogger(__name__)


class Pull(Command):
    """
    Pull code
    Usage:
        # pull special project
        python cobra.py pull --pid=project_id

        # pull all projects
        python cobra.py scan --all=true
    """
    option_list = (
        Option('--all', '-a', dest='is_all', required=False, help='Scan all projects'),
        Option('--pid', '-p', dest='pid', required=False, help='scan project id'),
    )

    def run(self, is_all=None, pid=None):
        if bool(is_all) is True:
            message = '[START] Pull all projects code'
            print(message)
            logging.info(message)
            projects = CobraProjects.query.with_entities(CobraProjects.repository).filter(CobraProjects.status == CobraProjects.get_status('on')).all()
            for project in projects:
                if '.git' not in project.repository:
                    continue
                code, msg, gg = scan.Scan(project.repository).pull_code()
                message = 'Pull code: {msg} {directory}'.format(msg=msg, directory=gg.repo_directory)
                if code == 1001:
                    logging.info(message)
                else:
                    logging.warning(message)
                print(message)
            message = '[END] Scan all projects'
            print(message)
            logging.info(message)
        elif pid is not None:
            project = CobraProjects.query.filter_by(id=pid).first()
            if project is None:
                message = 'Project not found'
                print(message)
                logging.critical(message)
            else:
                if '.git' not in project.repository:
                    message = 'Not git repository'
                    print(message)
                    logging.info(message)
                code, msg, gg = scan.Scan(project.repository).pull_code()
                message = 'Pull code: {msg} {directory}'.format(msg=msg, directory=gg.repo_directory)
                if code == 1001:
                    logging.info(message)
                else:
                    logging.warning(message)
                print(message)
        else:
            message = 'Please set --target param'
            print(message)
            logging.critical(message)
            sys.exit()
