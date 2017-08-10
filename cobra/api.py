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
import multiprocessing
import threading
from . import cli
from flask import Flask, request
from flask_restful import Api, Resource
from .engine import Running
from .log import logger
from .utils import md5, random_generator
from .config import Config

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue


def producer(task):
    q.put(task)


def consumer():
    while True:
        task = q.get()
        p = multiprocessing.Process(target=cli.start, args=task)
        p.start()
        p.join()
        q.task_done()


class AddJob(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        target = data.get("target")
        formatter = data.get("formatter")
        output = data.get("output")
        rule = data.get("rule")

        is_valid_key = key_verify(data=data)

        if is_valid_key is not True:
            return is_valid_key

        if not target or target == "":
            return {"code": 1002, "result": "URL cannot be empty."}

        if not formatter or formatter == '':
            formatter = 'json'
        if not output or output == '':
            output = ''
        if not rule or rule == '':
            rule = ''

        if isinstance(target, list):
            sids = list()
            for t in target:
                # Scan
                sid = get_sid(t)
                sids.append(sid)
                arg = (t, formatter, output, rule, sid)
                producer(task=arg)

            task_id = "something"

            result = {
                "msg": "Add scan job successfully.",
                "task_id": task_id,
                "sid": sids,
            }
        else:
            sid = get_sid(target)
            arg = (target, formatter, output, rule, sid)
            producer(task=arg)
            result = {
                "msg": "Add scan job successfully.",
                "sid": sid,
            }
        return {"code": 1001, "result": result}


class JobStatus(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        sid = data.get("sid")  # 需要拼接入路径，转为字符串

        is_valid_key = key_verify(data=data)

        if is_valid_key is not True:
            return is_valid_key

        if not sid or sid == "":
            return {"code": 1002, "result": "sid is required."}

        sid = str(data.get("sid"))  # 需要拼接入路径，转为字符串
        running = Running(sid)
        if running.is_file() is not True:
            data = {
                'code': 1001,
                'msg': 'scan id not exist!',
                'sid': sid,
                'status': 'no such scan',
                'report': ''
            }
        else:
            result = running.get()
            data = {
                'code': 1001,
                'msg': 'success',
                'sid': sid,
                'status': result['status'],
                'report': result['report']
            }
        return data


class ReportStatus(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        task_id = data.get("task_id")
        is_valid_key = key_verify(data=data)

        if is_valid_key is not True:
            return is_valid_key

        if not task_id or task_id == '':
            return {'code': 1002, 'result': 'task_id is required.'}

        task_id = str(data.get("task_id"))
        report = 'https://xxx.test.com'

        return {
            "code": 1001,
            "msg": "task done",
            "task_id": task_id,
            "report": report,
        }


def get_sid(target):
    sid = md5(target)[:5]
    sid = '{sid}{r}'.format(sid=sid, r=random_generator())
    return sid.lower()


def key_verify(data):
    key = Config(level1="cobra", level2="secret_key").value
    _key = data.get("key")

    if _key == key:
        return True
    elif not _key or _key == "":
        return {"code": 1002, "result": "Key cannot be empty."}
    elif not _key == key:
        return {"code": 4002, "result": "Key verify failed."}
    else:
        return {"code": 4002, "result": "Unknown key verify error."}


q = queue.Queue()


def start(host, port, debug):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    app = Flask(__name__)
    api = Api(app)

    api.add_resource(AddJob, '/api/add')
    api.add_resource(JobStatus, '/api/status')
    api.add_resource(ReportStatus, '/api/report')

    # 消费者线程
    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=consumer, args=()))

    for i in threads:
        i.setDaemon(daemonic=True)
        i.start()

    try:
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error as v:
        if v[0] == errno.EACCES:
            logger.critical('must root permission for start API Server!')
            exit()
        else:
            logger.critical('{msg}'.format(msg=v[1]))

    logger.info('API Server start success')
