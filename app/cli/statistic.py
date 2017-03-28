#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.statistic
    ~~~~~~~~~~~~~

    Implements CLI statistic

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import sys
import subprocess
from flask_script import Command, Option
from app.models import CobraTaskInfo
from app import db
from utils.log import logging

logging = logging.getLogger(__name__)


class Statistic(Command):
    """
    Statistics code-related information (lines of code / lines of comments / number of blank lines)
    Usage:
        python cobra.py statistic --target=project_directory --tid=task_id
    """
    option_list = (
        Option('--target', '-t', dest='target', help='directory'),
        Option('--tid', '-i', dest='tid', help='scan task id')
    )

    def run(self, target=None, tid=None):
        if target is None:
            logging.critical("Please set --target param")
            sys.exit()
        if tid is None:
            logging.critical("Please set --tid param")
            sys.exit()

        # Statistic Code
        p = subprocess.Popen(['cloc', target], stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        rs = output.split("\n")
        for r in rs:
            r_e = r.split()
            if len(r_e) > 3 and r_e[0] == 'SUM:':
                t = CobraTaskInfo.query.filter_by(id=tid).first()
                if t is not None:
                    t.code_number = r_e[4]
                    try:
                        db.session.add(t)
                        db.session.commit()
                        logging.info("Statistic code number done")
                    except Exception as e:
                        logging.error("Statistic code number failed" + str(e.message))
