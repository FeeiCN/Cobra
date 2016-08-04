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
from datetime import datetime
import argparse
import ConfigParser
import magic
from utils import log
from flask import request, jsonify, render_template
from werkzeug import secure_filename

from app import web, CobraTaskInfo, db, CobraProjects, CobraResults, CobraRules, CobraVuls


@web.route('/', methods=['GET'])
@web.route('/index', methods=['GET'])
def homepage():
    return render_template('index.html')


@web.route('/report/<int:id>', methods=['GET'])
def report(id):
    task_info = CobraTaskInfo.query.filter_by(id=id).first()
    if not task_info:
        return jsonify(status='4004', msg='report id not found')

    repository = task_info.target
    task_created_at = task_info.created_at
    project = CobraProjects.query.filter_by(repository=repository).first()
    project_name = project.name
    author = project.author
    project_description = project.remark
    time_consume = task_info.time_consume
    time_start = task_info.time_start
    time_end = task_info.time_end
    files = task_info.file_count
    code_number = task_info.code_number
    vulnerabilities_count = CobraResults.query.filter_by(task_id=id).count()
    results = CobraResults.query.filter_by(task_id=id).all()

    # convert timestamp to datetime
    time_start = time.strftime("%H:%M:%S", time.localtime(time_start))
    time_end = time.strftime("%H:%M:%S", time.localtime(time_end))

    # find rules -> vuls
    vulnerabilities = []
    for result in results:
        rules = CobraRules.query.filter_by(id=result.rule_id).first()
        vul_type = CobraVuls.query.filter_by(id=rules.vul_id).first().name

        find = False
        for each_vul in vulnerabilities:
            if each_vul['vul_type'] == vul_type:
                find = True
        if not find:
            vulnerabilities.append({'vul_type': vul_type, 'data': []})

        each_vul = {}
        each_vul['rule'] = rules.description
        each_vul['file'] = result.file
        each_vul['code'] = result.code
        each_vul['repair'] = rules.repair
        each_vul['line'] = result.line
        if rules.level == 3:
            each_vul['level'] = 'H'
            each_vul['color'] = 'red'
        elif rules.level == 2:
            each_vul['level'] = 'M'
            each_vul['color'] = 'orange'
        elif rules.level == 1:
            each_vul['level'] = 'L'
            each_vul['color'] = 'black'
        else:
            each_vul['level'] = 'Undefined'
            each_vul['color'] = '#555'

        for ev in vulnerabilities:
            if ev['vul_type'] == vul_type:
                ev['data'].append(each_vul)

    data = {
        'id': int(id),
        'project_name': project_name,
        'project_repository': repository,
        'project_description': project_description,
        'author': author,
        'task_created_at': task_created_at,
        'time_consume': str(time_consume) + 's',
        'time_start': time_start,
        'time_end': time_end,
        'files': files,
        'code_number': code_number,
        'vulnerabilities_count': vulnerabilities_count,
        'vulnerabilities': vulnerabilities,
    }
    return render_template('report.html', data=data)


@web.errorhandler(404)
def page_not_found():
    return render_template('404.html'), 404
