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
import time
import os
import json
import multiprocessing
import threading
from flask import Flask, request, render_template
from flask_restful import Api, Resource
from werkzeug.utils import secure_filename
from . import cli
from .cli import get_sid
from .engine import Running
from .log import logger
from .config import Config, running_path
from .utils import allowed_file

try:
    # Python 3
    import queue
except ImportError:
    # Python 2
    import Queue as queue

q = queue.Queue()
app = Flask(__name__, static_folder='templates/asset')


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

        # Report All Id
        a_sid = get_sid(target, True)
        if isinstance(target, list):
            for t in target:
                # Scan
                arg = (t, formatter, output, rule, a_sid)
                producer(task=arg)

            result = {
                "msg": "Add scan job successfully.",
                "sid": a_sid,
            }
        else:
            arg = (target, formatter, output, rule, a_sid)
            producer(task=arg)
            result = {
                "msg": "Add scan job successfully.",
                "sid": a_sid,
            }

        a_sid_data = {
            'sids': {}
        }
        running = Running(a_sid)

        # Write a_sid running data
        running.list(a_sid_data)

        # Write a_sid running status
        data = {
            'status': 'running',
            'report': ''
        }
        running.status(data)
        return {"code": 1001, "result": result}


class JobStatus(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "result": "Only support json, please post json data."}

        sid = data.get("sid")

        is_valid_key = key_verify(data=data)
        if is_valid_key is not True:
            return is_valid_key

        if not sid or sid == "":
            return {"code": 1002, "result": "sid is required."}

        sid = str(data.get("sid"))  # 需要拼接入路径，转为字符串
        running = Running(sid)
        if running.is_file() is not True:
            data = {
                'msg': 'scan id not exist!',
                'sid': sid,
                'status': 'no such scan',
                'report': ''
            }
        else:
            result = running.status()
            if result['status'] == 'running':
                r_data = running.list()
                ret = True
                for sid, git in r_data['sids'].items():
                    if Running(sid).is_file(True) is False:
                        ret = False
                if ret:
                    result['status'] = 'done'
                    running.status(result)
            data = {
                'msg': 'success',
                'sid': sid,
                'status': result['status'],
                'report': result['report']
            }
        return {"code": 1001, "result": data}


class FileUpload(Resource):
    @staticmethod
    def post():
        """
        Scan by uploading compressed files
        :return:
        """
        if 'file' not in request.files:
            return {'code': 1002, 'result': "File can't empty!"}
        file_instance = request.files['file']
        if file_instance.filename == '':
            return {'code': 1002, 'result': "File name can't empty!"}
        if file_instance and allowed_file(file_instance.filename):
            filename = secure_filename(file_instance.filename)

            if not os.path.isdir(os.path.join(Config(level1='upload', level2='directory').value, 'uploads')):
                os.mkdir(os.path.join(Config(level1='upload', level2='directory').value, 'uploads'))

            file_instance.save(os.path.join(os.path.join(Config(level1='upload', level2='directory').value, 'uploads'),
                                            filename))
            # Start scan
            code, result = 1001, 222
            return {'code': code, 'result': result}
        else:
            return {'code': 1002, 'result': "This extension can't support!"}


@app.route('/', methods=['GET', 'POST'])
def summary():
    a_sid = request.args.get(key='sid')
    if a_sid is None:
        key = Config(level1="cobra", level2="secret_key").value
        return render_template(template_name_or_list='index.html',
                               key=key)

    scan_status_file = os.path.join(running_path, '{sid}_status'.format(sid=a_sid))
    scan_list_file = os.path.join(running_path, '{sid}_list'.format(sid=a_sid))
    if not os.path.isfile(scan_status_file):
        return 'No such scan.'

    with open(scan_status_file, 'r') as f:
        scan_status = json.load(f).get('status')
    with open(scan_list_file, 'r') as f:
        scan_list = json.load(f).get('sids')

    if scan_status == 'running':
        return 'Scan job is still running, Please check later.'

    start_time = os.path.getctime(filename=scan_status_file)
    start_time = time.localtime(start_time)
    start_time = time.strftime('%Y-%m-%d %H:%M:%S', start_time)

    total_targets_number = len(scan_list)
    total_vul_number, critical_vul_number, high_vul_number, medium_vul_number, low_vul_number = 0, 0, 0, 0, 0
    rule_filter = dict()
    targets = list()
    for s_sid in scan_list.keys():
        target_info = dict()
        target_info.update({
            'sid': s_sid,
            'target': scan_list.get(s_sid),
        })
        s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
        with open(s_sid_file, 'r') as f:
            s_sid_data = json.load(f)
        total_vul_number += len(s_sid_data.get('vulnerabilities'))

        target_info.update({'total_vul_number': len(s_sid_data.get('vulnerabilities'))})
        target_info.update(s_sid_data)

        targets.append(target_info)

        for vul in s_sid_data.get('vulnerabilities'):
            if 9 <= int(vul.get('level')) <= 10:
                critical_vul_number += 1
            elif 6 <= int(vul.get('level')) <= 8:
                high_vul_number += 1
            elif 3 <= int(vul.get('level')) <= 5:
                medium_vul_number += 1
            elif 1 <= int(vul.get('level')) <= 2:
                low_vul_number += 1

            try:
                rule_filter[vul.get('rule_name')] += 1
            except KeyError:
                rule_filter[vul.get('rule_name')] = 1

    return render_template(template_name_or_list='summary.html',
                           total_targets_number=total_targets_number,
                           start_time=start_time,
                           targets=targets,
                           a_sid=a_sid,
                           total_vul_number=total_vul_number,
                           critical_vul_number=critical_vul_number,
                           high_vul_number=high_vul_number,
                           medium_vul_number=medium_vul_number,
                           low_vul_number=low_vul_number,
                           vuls=rule_filter, )


@app.route('/report/<path:a_sid>/<path:s_sid>', methods=['GET'])
def report(a_sid, s_sid):
    if s_sid is None:
        return 'No sid specified.'

    scan_data_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
    scan_list_file = os.path.join(running_path, '{sid}_list'.format(sid=a_sid))
    if not os.path.isfile(scan_data_file):
        return 'No such target.'

    with open(scan_data_file, 'r') as f:
        scan_data = json.load(f)
    with open(scan_list_file, 'r') as f:
        scan_list = json.load(f).get('sids')

    project_name = scan_list.get(s_sid).split('/')[-1].replace('.git', '')

    rule_filter = dict()
    for vul in scan_data.get('vulnerabilities'):
        rule_filter[vul.get('id')] = vul.get('rule_name')

    with open(os.path.join(os.path.dirname(__file__), 'templates/asset/js/report.js')) as f:
        report_js = f.read()

    return render_template(template_name_or_list='result.html',
                           scan_data=json.dumps(scan_data, ensure_ascii=False),
                           report_js=report_js,
                           target_filter=scan_list,
                           project_name=project_name,
                           rule_filter=rule_filter)


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


def start(host, port, debug):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    api = Api(app)

    api.add_resource(AddJob, '/api/add')
    api.add_resource(JobStatus, '/api/status')
    api.add_resource(FileUpload, '/api/upload')

    # consumer
    threads = []
    for i in range(10):
        threads.append(threading.Thread(target=consumer, args=()))

    for i in threads:
        i.setDaemon(daemonic=True)
        i.start()

    try:
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error as v:
        if v.errno == errno.EACCES:
            logger.critical('[{err}] must root permission for start API Server!'.format(err=v.strerror))
            exit()
        else:
            logger.critical('{msg}'.format(msg=v.strerror))

    logger.info('API Server start success')
