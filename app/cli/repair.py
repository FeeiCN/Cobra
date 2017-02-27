#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.repair
    ~~~~~~~~~~

    Implements CLI repair

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import sys
from flask_script import Command, Option
from app.models import CobraProjects, CobraWhiteList
from app.models import CobraResults, CobraRules, CobraVuls
from engine.core import Core
from pickup.git import Git
from app import db
from utils.log import logging

logging = logging.getLogger(__name__)

class Repair(Command):
    """
    Detection of existing vulnerabilities to repair the situation
    Usage:
        python cobra.py repair --pid=your_project_id
    """
    option_list = (
        Option('--pid', '-p', dest='pid', help='scan project id'),
    )

    def run(self, pid=None):
        if pid is None:
            logging.critical("Please set --pid param")
            sys.exit()
        # Project info
        project_info = CobraProjects.query.filter_by(id=pid).first()
        if project_info.repository[0] == '/':
            project_directory = project_info.repository
        else:
            project_directory = Git(project_info.repository).repo_directory
        # Third-party ID
        vuln_all = CobraVuls.query.all()
        vuln_all_d = {}
        for vuln in vuln_all:
            vuln_all_d[vuln.id] = vuln.third_v_id
        # Not fixed vulnerabilities
        result_all = db.session().query(CobraRules, CobraResults).join(CobraResults, CobraResults.rule_id == CobraRules.id).filter(
            CobraResults.project_id == pid,
            CobraResults.status < 2
        ).all()
        for index, (rule, result) in enumerate(result_all):
            # Rule
            result_info = {
                'task_id': result.task_id,
                'project_id': result.project_id,
                'project_directory': project_directory,
                'rule_id': result.rule_id,
                'result_id': result.id,
                'file_path': result.file,
                'line_number': result.line,
                'code_content': result.code,
                'third_party_vulnerabilities_name': rule.description,
                'third_party_vulnerabilities_type': vuln_all_d[rule.vul_id]
            }
            # White list
            white_list = []
            ws = CobraWhiteList.query.with_entities(CobraWhiteList.path).filter_by(project_id=result.project_id, rule_id=result.rule_id, status=1).all()
            if ws is not None:
                for w in ws:
                    white_list.append(w.path)
            Core(result_info, rule, project_info.name, white_list).repair()
