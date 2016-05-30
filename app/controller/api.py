#!/usr/bin/env python
# coding: utf-8

import time

from flask import request, jsonify

from app import web
from app import CobraTaskInfo
from app import db


# default api url
API_URL = '/api'


@web.route(API_URL + '/add_new_task', methods=['POST'])
def add_new_task():
    """ Add a new task api.
    post json to http://url/api/add_new_task
    example:
        {
            "url": "https://gitlab.com/username/project",   // must, gitlab address
            "branch": "master",                             // must, the project branch
            "username": "your username",    // optional, the username access to the repo. If the repo is public, leave this blank.
            "password": "your password",    // optional, the password access to the repo. If the repo is public, leave this blank.
            "old_version": "old version here",  // optional, if you choice diff scan mode, you should provide old version hash.
            "new_version": "new version here",  // optional, if you choice diff scan mode, you should provide new version hash.
            "scan_way": 1,      // must, scan way, 1-full scan, 2-diff scan, if you want to use full scan mode,
                                // leave old_version and new_version blank.
            "scan_type": 2,     // must, scan type, 1-all vulnerabilities, 2-general vulnerabilities, 3-code syntax
            "level": "1",       // must, scan level, 1-5
        }
    :return:
        The return value also in json format, usually is:
        {"code": 1001, "msg": "error reason or success."}
        code: 1004: Unknown error, if you see this error code, most time is cobra's database error.
        code: 1003: You support the parameters is not json.
        code: 1002: Some parameters is empty. More information in "msg".
        code: 1001: Success, no error.
    """
    data = request.json
    if not data or data == "":
        return jsonify(code=1003, msg=u'Only support json, please post json data.')

    # get data
    url = data.get('url')
    branch = data.get('branch')
    username = data.get('username')
    password = data.get('password')
    new_version = data.get('new_version')
    old_version = data.get('old_version')
    scan_way = data.get('scan_way')
    scan_type = data.get('scan_type')
    level = data.get('level')

    # check data
    if not url or url == "":
        return jsonify(code=1002, msg=u'url can not be empty.')
    if not branch or branch == "":
        return jsonify(code=1002, msg=u'branch can not be empty.')
    if not scan_way or scan_way == "":
        return jsonify(code=1002, msg=u'scan way can not be empty')
    if not scan_type or scan_type == "":
        return jsonify(code=1002, msg=u'scan type can not be empty')
    if not level or level == "":
        return jsonify(code=1002, msg=u'level can not be empty')

    current_time = int(time.time())
    task_info = CobraTaskInfo(task_type=1, create_time=current_time, filename=None, url=url, branch=branch,
                              username=username, password=password, scan_type=scan_type, level=level, scan_way=scan_way,
                              old_version=old_version, new_version=new_version)
    try:
        db.session.add(task_info)
        db.session.commit()
        return jsonify(code=1001, msg=u'task add success.')
    except:
        return jsonify(code=1004, msg=u'Unknown error, try again later?')

