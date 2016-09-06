# -*- coding: utf-8 -*-

"""
    controller.api
    ~~~~~~~~~~~~~~

    Implements api for app controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
from utils import config, common
from flask import request, jsonify
from werkzeug.utils import secure_filename
from app import web, CobraAuth, CobraTaskInfo, CobraProjects
from engine import scan

# default api url
API_URL = '/api'

"""
https://github.com/wufeifei/cobra/wiki/API
"""


@web.route(API_URL + '/add', methods=['POST'])
def add_task():
    """ Add a new task api.
    post json to http://url/api/add_new_task
    example:
        {
            "key": "34b9a295d037d47eec3952e9dcdb6b2b",              // must, client key
            "target": "https://gitlab.com/username/project.git",    // must, gitlab address
            "branch": "master",                                     // must, the project branch
            "old_version": "old version here",                      // optional, if you choice diff scan mode, you should provide old version hash.
            "new_version": "new version here",                      // optional, if you choice diff scan mode, you should provide new version hash.
        }
    :return:
        The return value also in json format, usually is:
        {"code": 1001, "result": "error reason or success."}
        code: 1005: Unknown Protocol
        code: 1004: Unknown error, if you see this error code, most time is cobra's database error.
        code: 1003: You support the parameters is not json.
        code: 1002: Some parameters is empty. More information in "msg".
        code: 1001: Success, no error.
    """
    data = request.json
    if not data or data == "":
        return jsonify(code=1003, result=u'Only support json, please post json data.')

    key = data.get('key')

    auth = CobraAuth.query.filter_by(key=key).first()
    if auth is None:
        return jsonify(code=4002, result=u'Key verify failed')
    target = data.get('target')
    branch = data.get('branch')
    new_version = data.get('new_version')
    old_version = data.get('old_version')

    project_id = data.get('project_id')
    if project_id:
        project = CobraProjects.query.filter_by(id=project_id).first()
        if not project:
            return jsonify(code=1002, result=u'not find the project.')
        target = project.repository
        branch = 'master'
        new_version = ""
        old_version = ""

    # verify key
    if not key or key == "":
        return jsonify(code=1002, result=u'key can not be empty.')
    if not target or target == "":
        return jsonify(code=1002, result=u'url can not be empty.')
    if not branch or branch == "":
        return jsonify(code=1002, result=u'branch can not be empty.')

    code, result = scan.Scan(target).version(branch, new_version, old_version)
    return jsonify(code=code, result=result)


@web.route(API_URL + '/status', methods=['POST'])
def status_task():
    scan_id = request.json.get('scan_id')
    key = request.json.get('key')
    auth = CobraAuth.query.filter_by(key=key).first()
    if auth is None:
        return jsonify(code=4002, result=u'Key verify failed')
    c = CobraTaskInfo.query.filter_by(id=scan_id).first()
    if not c:
        return jsonify(status=4004)
    status = {
        0: 'init',
        1: 'scanning',
        2: 'done',
        3: 'error'
    }
    status_text = status[c.status]
    domain = config.Config('cobra', 'domain').value
    result = {
        'status': status_text,
        'text': 'Success',
        'report': 'http://' + domain + '/report/' + str(scan_id),
        'allow_deploy': True
    }
    return jsonify(status=1001, result=result)


@web.route(API_URL + '/upload', methods=['POST'])
def upload_file():
    # check if the post request has the file part
    if 'file' not in request.files:
        return jsonify(code=1002, result="File can't empty!")
    file_instance = request.files['file']
    if file_instance.filename == '':
        return jsonify(code=1002, result="File name can't empty!")
    if file_instance and common.allowed_file(file_instance.filename):
        filename = secure_filename(file_instance.filename)
        file_instance.save(os.path.join(os.path.join(config.Config('upload', 'directory').value, 'uploads'), filename))
        # scan job
        code, result = scan.Scan(filename).compress()
        return jsonify(code=code, result=result)
    else:
        return jsonify(code=1002, result="This extension can't support!")
