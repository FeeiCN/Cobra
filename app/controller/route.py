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
import argparse
import ConfigParser

import magic
from utils import log
from flask import request, jsonify, render_template
from werkzeug import secure_filename

from app import web, CobraTaskInfo, db, CobraProjects


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
        username = request.form['username'] if request.form['username'] != '' else None
        password = request.form['password'] if request.form['password'] != '' else None
        branch = request.form['branch'] if request.form['branch'] != '' else 'master'

        if not url:
            return jsonify(code=1002, msg=u'please support gitlab url. '
                                          u'If this is a public repo, just leave username and password blank')

        # insert into db
        new_task = CobraTaskInfo(task_type, int(time.time()), None, url, branch, scan_way, old_version, new_version)
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

        new_task = CobraTaskInfo(task_type, int(time.time()), filename, None, None, scan_way, old_version, new_version)
        db.session.add(new_task)
        db.session.commit()
    return jsonify(code=1001, msg=u'success', id=123)


@web.route('/status/<int:id>', methods=['GET'])
def status(id):
    log.debug('In status Route')
    return jsonify(code=1001, msg='success', status='running')


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
