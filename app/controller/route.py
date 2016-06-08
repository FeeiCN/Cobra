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
    log.debug('In homepage Route')
    return render_template('index.html')


@web.route('/blank')
def blank():
    log.debug('In blank Route')
    return render_template('blank.html')


# @web.route('/api/add', methods=['POST'])
# def add():
#     log.debug('In api/add Route')
#     key = request.form['key']
#     name = request.form['name']
#     type = request.form['type']
#     repository = request.form['repository']
#     branch = request.form['branch']
#     version = request.form['version']
#     old_version = request.form['old_version']
#     files = request.form['files']
#     author = request.form['author']
#
#     repo_type = 1
#     CobraProjects(name, repo_type, repository, branch)


@web.route('/add', methods=['POST'])
def add():
    log.debug('In add Route')
    # url, username, password, scan_way, old_version, new_version
    # if user upload a file, so we set the scan type to file scan
    # if there is no upload file, we set the scan type to gitlab scan

    # check scan way and version
    scan_way = request.form['scan_way']
    old_version = request.form['old_version']
    new_version = request.form['new_version']
    if not scan_way or not scan_way.isdigit():
        return jsonify(code=1002, msg=u'please select scan method.')

    if scan_way == '2':
        if not old_version or not new_version:
            return jsonify(code=1002, msg=u'in diff mode, please provide new version and old version.')
    elif scan_way == '1':
        old_version = None
        new_version = None
    else:
        return jsonify(code=1002, msg=u'scan method error.')

    task_type = 1
    # check if there is a file or gitlab url
    if len(request.files) == 0:
        # no files, should check username and password
        task_type = 1
        url = request.form['repository']
        branch = request.form['branch'] if request.form['branch'] != '' else 'master'

        if not url:
            return jsonify(code=1002, msg=u'please support gitlab url. '
                                          u'If this is a public repo, just leave username and password blank')

        # insert into db
        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_task = CobraTaskInfo(task_type, None, url, branch, scan_way, old_version, new_version, current_time,
                                 current_time)
        db.session.add(new_task)
        db.session.commit()
    else:
        # there is a file, check file format and uncompress it.
        # get uploads directory
        config = ConfigParser.ConfigParser()
        config.read('config')
        upload_directory = config.get('cobra', 'upload_directory') + os.sep
        if os.path.isdir(upload_directory) is not True:
            os.mkdir(upload_directory)
        task_type = 2
        upload_src = request.files['file']
        filename = str(int(time.time())) + '_' + secure_filename(upload_src.filename)
        filepath = upload_directory + filename
        upload_src.save(filepath)

        # if you upload a rar file, upload_src.mimetype will returns "application/octet-stream"
        # rather than "application/x-rar"
        # check file type via mime type
        file_type = magic.from_file(filepath, mime=True)
        if file_type != 'application/x-rar' and file_type != 'application/x-gzip' and file_type != 'application/zip':
            os.remove(filepath)
            return jsonify(code=1002, msg=u'only rar, zip and tar.gz supported.')

        current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        new_task = CobraTaskInfo(task_type, filename, None, None, scan_way, old_version, new_version, current_time,
                                 current_time)
        db.session.add(new_task)
        db.session.commit()
    return jsonify(code=1001, msg=u'success', id=123)


@web.route('/status/<int:id>', methods=['GET'])
def status(id):
    log.debug('In status Route')
    return jsonify(code=1001, msg='success', status='running')


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
    scan_time = task_info.time_consume
    date = task_info.time_start
    files = task_info.file_count
    vulnerabilities_count = CobraResults.query.filter_by(task_id=id).count()
    results = CobraResults.query.filter_by(task_id=id).all()

    # convert timestamp to datetime
    date = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(date))

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
        'author': author,
        'date': date,
        'task_created_at': task_created_at,
        'scan_time': scan_time,
        'files': files,
        'vulnerabilities_count': vulnerabilities_count,
        'vulnerabilities': vulnerabilities,
    }
    return render_template('report.html', data=data)


@web.errorhandler(404)
def page_not_found(e):
    log.debug('In 404 Route')
    return render_template('404.html'), 404


def parse_option(self):
    parser = argparse.ArgumentParser(description='Cobra is a open source Code Security Scan System')
    parser.add_argument('string', metavar='project/path', type=str, nargs='+', help='Project Path')
    parser.add_argument('--version', help='Cobra Version')
    args = parser.parse_args()
    print args.string[0]
