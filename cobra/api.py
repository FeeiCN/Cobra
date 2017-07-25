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
import subprocess
from flask import Flask, request
from flask_restful import Api, Resource
from .engine import Running
from .log import logger
from .utils import md5, random_generator
from .config import Config, cobra_main


class AddJob(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        key = Config(level1="cobra", level2="secret_key").value
        _key = data.get("key")
        target = data.get("target")
        formatter = data.get("formatter")
        output = data.get("output")
        rule = data.get("rule")

        if not _key or _key == "":
            return {"code": 1002, "result": "Key cannot be empty."}
        elif not _key == key:
            return {"code": 4002, "result": "Key verify failed."}

        if not target or target == "":
            return {"code": 1002, "result": "URL cannot be empty."}

        if not formatter or formatter == '':
            formatter = 'json'
        if not output or output == '':
            output = ''
        if not rule or rule == '':
            rule = ''

        # Scan
        sid = get_sid(target)
        subprocess.Popen(
            ['python', cobra_main, "-t", str(target), "-f", str(formatter), "-o", str(output), '-r', str(rule), '-sid',
             str(sid)])
        result = {
            'msg': 'Add scan job successfully',
            'scan_id': sid
        }
        return {"code": 1001, "result": result}


class JobStatus(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        scan_id = str(data.get("scan_id"))  # 需要拼接入路径，转为字符串

        key = Config(level1="cobra", level2="secret_key").value
        _key = request.json.get("key")

        if not _key or _key == "":
            return {"code": 1002, "result": "Key cannot be empty."}
        elif not _key == key:
            return {"code": 4002, "result": "Key verify failed."}

        running = Running(scan_id)
        if running.is_file() is not True:
            data = {
                'code': 1001,
                'msg': 'scan id not exist!',
                'scan_id': scan_id,
                'status': 'done',
                'report': ''
            }
        else:
            result = running.get()
            data = {
                'code': 1001,
                'msg': 'success',
                'scan_id': scan_id,
                'status': result['status'],
                'report': result['report']
            }
        return data


def get_sid(target):
    sid = md5(target)[:5]
    sid = '{sid}{r}'.format(sid=sid, r=random_generator())
    return sid.lower()


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
            logger.critical('must root permission for start API Server!')
            exit()
        else:
            logger.critical('{msg}'.format(msg=v[1]))

    logger.info('API Server start success')
