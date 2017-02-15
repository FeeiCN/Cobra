#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.scan
    ~~~~~~~~

    Implements CLI scan

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import sys
import time
import logging
from flask_script import Command, Option
from app.models import CobraTaskInfo
from app import db


class Scan(Command):
    """
    Scan for vulnerabilities
    Usage:
        python cobra.py scan --target=project_directory --tid=task_id --pid=project_id
    """
    option_list = (
        Option('--target', '-t', dest='target', help='scan target(directory/git repository/svn url/file path)'),
        Option('--tid', '-i', dest='tid', help='scan task id'),
        Option('--pid', '-p', dest='pid', help='scan project id'),
    )

    def run(self, target=None, tid=None, pid=None):
        if target is None:
            logging.critical("Please set --target param")
            sys.exit()
        if tid is not None:
            task_id = tid
            # Start Time For Task
            t = CobraTaskInfo.query.filter_by(id=tid).first()
            if t is None:
                logging.critical("Task id doesn't exists.")
                sys.exit()
            if t.status not in [0, 1]:
                logging.critical("Task Already Scan.")
                sys.exit()
            t.status = 1
            t.time_start = int(time.time())
            t.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
            try:
                db.session.add(t)
                db.session.commit()
            except Exception as e:
                logging.error("Set start time failed" + str(e.message))
        else:
            task_id = None

        if os.path.isdir(target) is not True:
            logging.critical('Target is not directory')
            sys.exit()
        from engine import static
        static.Static(target, task_id=task_id, project_id=pid).analyse()
