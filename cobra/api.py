# -*- coding: utf-8 -*-

"""
    api
    ~~~

    Implements API Server and Interface

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import socket
import errno
from flask import Flask, request
from flask_restful import Api, Resource
from .log import logger
from .config import Config


key = Config(level1="cobra", level2="secret_key").value


class AddJob(Resource):
    def post(self):
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        _key = data.get("key")
        target = data.get("target")
        branch = data.get("branch")
        new_version = data.get(k="new_version", default="")
        old_version = data.get(k="old_version", default="")

        if not _key or _key == "":
            return {"code": 1002, "result": "Key cannot be empty."}
        elif not _key == key:
            return {"code": 4002, "result": "Key verify failed."}

        if not target or target == "":
            return {"code": 1002, "result": "URL cannot be empty."}

        if not branch or branch == "":
            return {"code": 1002, "result": "Branch cannot be empty."}

        # TODO begin scan...


class JobStatus(Resource):
    def post(self):
        scan_id = request.json.get("scan_id")
        _key = request.json.get("key")

        if not _key or _key == "":
            return {"code": 1002, "result": "Key cannot be empty."}
        elif not _key == key:
            return {"code": 4002, "result": "Key verify failed."}

        status = {
            0: "init",
            1: "scanning",
            2: "done",
            3: "error",
        }
        return {"scan_id": scan_id, "status": "running"}


def start(host, port, debug):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(AddJob, '/api/add')
    api.add_resource(JobStatus, '/api/status')
    try:
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error, v:
        if v[0] == errno.EACCES:
            logger.critical('must sudo permission for start RESTful server!')
            exit()
        else:
            logger.critical('{msg}'.format(msg=v[1]))

    logger.info('RESTful server start success')
