#!/usr/bin/env python
# coding: utf-8

import time

from flask import request, jsonify

from app import web
from app import CobraTaskInfo
from app import CobraProjects
from app import db
from pickup import GitTools


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
            "username": "username here",        // if the repo is private, please provide the account username
            "password": "password here",        // if the repo is private, please provide the account password
            "old_version": "old version here",  // optional, if you choice diff scan mode, you should provide old version hash.
            "new_version": "new version here",  // optional, if you choice diff scan mode, you should provide new version hash.
            "scan_way": 1,      // must, scan way, 1-full scan, 2-diff scan, if you want to use full scan mode,
                                // leave old_version and new_version blank.
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
    new_version = data.get('new_version')
    old_version = data.get('old_version')
    username = data.get('username')
    password = data.get('password')
    scan_way = data.get('scan_way')

    # check data
    if not url or url == "":
        return jsonify(code=1002, msg=u'url can not be empty.')
    if not branch or branch == "":
        return jsonify(code=1002, msg=u'branch can not be empty.')
    if not scan_way or scan_way == "":
        return jsonify(code=1002, msg=u'scan way can not be empty')

    current_time = time.strftime('%Y-%m-%d %X', time.localtime())
    gg = GitTools.Git(url, branch=branch, username=username, password=password)
    repo_author = gg.repo_author
    repo_name = gg.repo_name

    new_version = None if new_version == "" else new_version
    old_version = None if old_version == "" else old_version
    username = None if username == "" else username
    password = None if password == "" else password

    # TODO: file count

    # insert into task info table.
    task = CobraTaskInfo(url, branch, scan_way, new_version, old_version, None, None, None, 1,
                         current_time, current_time)

    p = CobraProjects.query.filter_by(repository=url).first()
    project = None
    if not p:
        # insert into project table.
        project = CobraProjects(url, repo_name, repo_author, None, None, current_time, current_time)

    try:
        db.session.add(task)
        if not p:
            db.session.add(project)
        db.session.commit()
        return jsonify(code=1001, msg=u'task add success.')
    except:
        return jsonify(code=1004, msg=u'Unknown error, try again later?')

