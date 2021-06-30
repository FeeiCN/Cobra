# -*- coding: utf-8 -*-

"""
    api
    ~~~

    Implements API Server and Interface

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import datetime
import errno
import json
import multiprocessing
import os
import re
import socket
import subprocess
import threading
import time
import traceback

import requests
from flask import Flask, request, render_template, Blueprint
from flask_restful import Api, Resource, reqparse
from werkzeug.urls import url_unquote

from . import cli
from .cli import get_sid
from .config import Config, running_path, package_path
from .engine import Running
from .log import logger
from .utils import allowed_file, secure_filename, PY2, split_branch

try:
    # Python 3
    import queue
    from urllib.parse import urlparse, quote_plus
except ImportError:
    # Python 2
    import Queue as queue
    from urlparse import urlparse
    from urllib import quote_plus

q = queue.Queue()
app = Flask(__name__, static_folder='templates/asset')
running_host = '0.0.0.0'
running_port = 5000


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
            return {"code": 1003, "msg": "Only support json, please post json data."}

        target = data.get("target")
        formatter = data.get("formatter")
        output = data.get("output")
        rule = data.get("rule")
        is_del = data.get("dels")

        is_valid_key = key_verify(data=data)

        if is_valid_key is not True:
            return is_valid_key

        if not target or target == "":
            return {"code": 1002, "msg": "URL cannot be empty."}

        if not formatter or formatter == '':
            formatter = 'json'
        if not output or output == '':
            output = ''
        if not rule or rule == '':
            rule = ''
        if not is_del or is_del == '':
            is_del = False

        # Report All Id
        a_sid = get_sid(target, True)
        running = Running(a_sid)

        # Write a_sid running data
        running.init_list(data=target)

        # Write a_sid running status
        data = {
            'status': 'running',
            'report': ''
        }
        running.status(data)

        if isinstance(target, list):
            for t in target:
                # Scan
                if re.match(r'http://|https://', t):
                    arg = (t, formatter, output, rule, a_sid, is_del)
                    producer(task=arg)

                else:
                    return {"code": 1004, "msg": "Please input a valid URL"}

            result = {
                'msg': 'Add scan job successfully.',
                'sid': a_sid,
                'total_target_num': len(target),
            }
        else:
            if re.match(r'http://|https://', target):
                arg = (target, formatter, output, rule, a_sid, is_del)
                producer(task=arg)

            else:
                return {"code": 1004, "msg": "Please input a valid URL"}

            result = {
                'msg': 'Add scan job successfully.',
                'sid': a_sid,
                'total_target_num': 1,
            }

        return {"code": 1001, "result": result}


class JobStatus(Resource):
    @staticmethod
    def post():
        data = request.json
        if not data or data == "":
            return {"code": 1003, "msg": "Only support json, please post json data."}

        sid = data.get("sid")

        is_valid_key = key_verify(data=data)
        if is_valid_key is not True:
            return is_valid_key

        if not sid or sid == "":
            return {"code": 1002, "msg": "sid is required."}

        sid = str(data.get("sid"))  # 需要拼接入路径，转为字符串
        running = Running(sid)
        if running.is_file() is not True:
            data = {
                'code': 1004,
                'msg': 'scan id does not exist!',
                'sid': sid,
                'status': 'no such scan',
                'report': ''
            }
            return data
        else:
            result = running.status()
            r_data = running.list()
            allow_deploy = True
            total_vul_number = critical_vul_number = high_vul_number = medium_vul_number = low_vul_number = 0
            if result['status'] == 'running':
                ret = True
                result['still_running'] = dict()
                for s_sid, git in r_data['sids'].items():
                    if Running(s_sid).is_file(True) is False:
                        result['still_running'].update({s_sid: git})
                        ret = False
                if ret:
                    result['status'] = 'done'
                    running.status(result)
            elif result['status'] == 'done':
                # 统计各类漏洞数量，并给出上线风险评估
                targets = list()

                scan_list = Running(sid).list()
                for s_sid, target_str in scan_list.get('sids').items():
                    target_info = dict()

                    # 分割项目地址与分支，默认 master
                    target, branch = split_branch(target_str)

                    target_info.update({
                        'sid': s_sid,
                        'target': target,
                        'branch': branch,
                    })
                    s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
                    with open(s_sid_file, 'r') as f:
                        s_sid_data = json.load(f)
                        if s_sid_data.get('code') != 1001:
                            continue
                        else:
                            s_sid_data = s_sid_data.get('result')
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
                if critical_vul_number > 0:
                    allow_deploy = False

            data = {
                'msg': 'success',
                'sid': sid,
                'status': result.get('status'),
                'report': request.url_root + result.get('report'),
                'still_running': result.get('still_running'),
                'total_target_num': r_data.get('total_target_num'),
                'statistic': {
                    'critical': critical_vul_number,
                    'high': high_vul_number,
                    'medium': medium_vul_number,
                    'low': low_vul_number
                },
                'allow_deploy': allow_deploy,
                'not_finished': int(r_data.get('total_target_num')) - len(r_data.get('sids')) + len(result.get('still_running')),
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
            dst_directory = os.path.join(package_path, filename)
            file_instance.save(dst_directory)
            # Start scan
            a_sid = get_sid(dst_directory, True)
            data = {
                'status': 'running',
                'report': ''
            }
            Running(a_sid).status(data)
            try:
                cli.start(dst_directory, None, 'stream', None, a_sid=a_sid)
            except Exception as e:
                traceback.print_exc()
            code, result = 1001, {'sid': a_sid}
            return {'code': code, 'result': result}
        else:
            return {'code': 1002, 'result': "This extension can't support!"}


class ResultData(Resource):
    @staticmethod
    def post():
        """
        pull scan result data.
        :return:
        """
        data = request.json
        if not data or data == "":
            return {"code": 1003, "msg": "Only support json, please post json data."}

        s_sid = data.get('sid')
        if not s_sid or s_sid == "":
            return {"code": 1002, "msg": "sid is required."}

        s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
        if not os.path.exists(s_sid_file):
            return {'code': 1002, 'msg': 'No such target.'}

        with open(s_sid_file, 'r') as f:
            scan_data = json.load(f)
            if scan_data.get('code') == 1001:
                scan_data = scan_data.get('result')
            else:
                return {
                    'code': scan_data.get('code'),
                    'msg': scan_data.get('msg'),
                }

        rule_filter = dict()
        for vul in scan_data.get('vulnerabilities'):
            rule_filter[vul.get('id')] = vul.get('rule_name')

        return {
            'code': 1001,
            'result': {
                'scan_data': scan_data,
                'rule_filter': rule_filter,
            }
        }


class ResultDetail(Resource):
    @staticmethod
    def post():
        """
        get vulnerable file content
        :return:
        """
        data = request.json
        if not data or data == "":
            return {'code': 1003, 'msg': 'Only support json, please post json data.'}

        sid = data.get('sid')
        file_path = url_unquote(data.get('file_path'))

        if not sid or sid == '':
            return {"code": 1002, "msg": "sid is required."}

        if not file_path or file_path == '':
            return {'code': 1002, 'msg': 'file_path is required.'}

        s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=sid))
        if not os.path.exists(s_sid_file):
            return {'code': 1002, 'msg': 'No such target.'}

        with open(s_sid_file, 'r') as f:
            target_directory = json.load(f).get('result').get('target_directory')

        if not target_directory or target_directory == '':
            return {'code': 1002, 'msg': 'No such directory'}

        if PY2:
            file_path = map(secure_filename, [path.decode('utf-8') for path in file_path.split('/')])
        else:
            file_path = map(secure_filename, [path for path in file_path.split('/')])

        filename = target_directory
        for _dir in file_path:
            filename = os.path.join(filename, _dir)
        if os.path.exists(filename):
            extension = guess_type(filename)
            if is_text(filename):
                with open(filename, 'r') as f:
                    file_content = f.read()
            else:
                file_content = 'This is a binary file.'
        else:
            return {'code': 1002, 'msg': 'No such file.'}

        return {'code': 1001, 'result': {'file_content': file_content, 'extension': extension}}


class Search(Resource):
    @staticmethod
    def post():
        """
        Search specific rule.
        :return:
        """
        data = request.json
        if not data or data == "":
            return {'code': 1003, 'msg': 'Only support json, please post json data.'}

        sid = data.get('sid')
        if not sid or sid == '':
            return {'code': 1002, 'msg': 'sid is required.'}

        rule_id = data.get('rule_id')
        if not rule_id or rule_id == '':
            return {'code': 1002, 'msg': 'rule_id is required.'}

        scan_list_file = os.path.join(running_path, '{sid}_list'.format(sid=sid))
        if not os.path.exists(scan_list_file):
            return {'code': 1002, 'msg': 'No such sid.'}

        with open(scan_list_file, 'r') as f:
            scan_list = json.load(f)

        if not isinstance(rule_id, list):
            rule_id = [rule_id]

        search_data = list()
        for s_sid in scan_list.get('sids').keys():
            target, branch = split_branch(scan_list.get('sids').get(s_sid))
            search_result = search_rule(s_sid, rule_id)
            cvi_count = list(search_result.values())
            if int(cvi_count[0]) > 0:
                search_data.append({
                    'target_info': {
                        'sid': s_sid,
                        'target': target,
                        'branch': branch,
                    },
                    'search_result': search_result,
                })

        return {
            'code': 1001,
            'result': search_data,
        }


class GetMemeber(Resource):
    parser = reqparse.RequestParser()
    parser.add_argument('repo-url', type=str, required=True, help='repo-url 不能为空，格式为 http://xxx.xxx.com/user/reponame.git')

    def get(self):
        """
        从 GitLab API 获取项目负责人
        :return:
        """
        data = self.parser.parse_args()
        repo_url = data.get('repo-url')
        url_parser = urlparse(repo_url)

        if 'gitlab' in url_parser.netloc:
            _, members = self.get_member(url_parser=url_parser)
            if _:
                if members:
                    return {
                        'code': 1001,
                        'result': {
                            'members': members,
                        },
                    }
                else:
                    return {
                        'code': 1002,
                        'msg': 'Empty members',
                    }
            else:
                return {
                    'code': 1002,
                    'msg': members
                }
        else:
            return {
                'code': 1002,
                'msg': 'Not support repo type'
            }

    @staticmethod
    def get_member(url_parser):
        """
        请求 GitLab API
        :param url_parser: urlparse(repo_url)
        :return:
        """
        domain = url_parser.netloc
        scheme = url_parser.scheme
        repo = re.sub(r"\.git.*", "", url_parser.path)
        # 去掉 repo 开头的 /
        repo = repo[1:] if repo.startswith('/') else repo
        api_url = scheme + '://' + domain + '/api/v3/projects/' + quote_plus(repo) + '/members'

        try:
            private_token = Config(level1="git", level2="private_token").value
            if private_token == '':
                return False, 'No private token specified'

            header = {
                'PRIVATE-TOKEN': private_token
            }
            data = requests.get(url=api_url, headers=header, timeout=3).json()
            members = []
            for m in data:
                members.append(m.get('username'))
            return True, members
        except Exception as e:
            return False, str(e)


@app.route('/report', methods=['GET'])
def report():
    """
    get report
    :return:
    """
    data_lists = []
    total_files = 0
    total_vul_number = critical_vul_number = high_vul_number = medium_vul_number = low_vul_number = 0
    rule_num = dict()
    target_directorys = []
    time_range = {}
    time_start = request.args.get(key='start')
    time_end = request.args.get(key='end')

    if time_start is None and time_end is None:
        time_start = datetime.datetime.today() + datetime.timedelta(days=-7)
        time_end = datetime.datetime.today().strftime("%Y-%m-%d")
        time_start = time_start.strftime("%Y-%m-%d")

    if time_start is not None and time_end is not None:
        if PY2:
            time_start = time_start.encode('utf-8')
            time_end = time_end.encode('utf-8')

    if time_start is not '' and time_end is not '':
        time_str = "%Y-%m-%d"
        date_time_str = "%m-%d"
        t_start = datetime.datetime.strptime(time_start, time_str)
        t_end = datetime.datetime.strptime(time_end, time_str)
        t_end += datetime.timedelta(days=1)

        t_start_tuple = t_start.timetuple()
        t_end_tuple = t_end.timetuple()

        t_start_un = time.mktime(t_start_tuple)
        t_end_un = time.mktime(t_end_tuple)

        while t_start < t_end:
            time_range[t_start.strftime(date_time_str)] = 0
            t_start += datetime.timedelta(days=1)

        for data_file in os.listdir(running_path):
            if re.match(r'.*_data', data_file):
                data = os.path.join(running_path, data_file)
                data_time = os.path.getctime(filename=data)
                if t_start_un < data_time < t_end_un:
                    data_time = time.strftime(date_time_str, time.localtime(data_time))
                    with open(data, 'r') as f:
                        try:
                            data_content = json.load(f)
                        except json.JSONDecodeError:
                            logger.warning('[REPORT] Delete empty data file: {}'.format(data_file))
                            os.remove(data)
                            continue
                    data_results = data_content.get('result')
                    if data_results:
                        target_directory = data_results.get('target_directory')
                        if target_directory in target_directorys:
                            continue
                        else:
                            target_directorys.append(target_directory)

                        data_lists.append(data)
                        total_files += data_results.get('file')
                        total_vul_number += len(data_results.get('vulnerabilities'))
                        time_range[data_time] += len(data_results.get('vulnerabilities'))

                        for vul in data_results.get('vulnerabilities'):
                            if 9 <= int(vul.get('level')) <= 10:
                                critical_vul_number += 1
                            elif 6 <= int(vul.get('level')) <= 8:
                                high_vul_number += 1
                            elif 3 <= int(vul.get('level')) <= 5:
                                medium_vul_number += 1
                            elif 1 <= int(vul.get('level')) <= 2:
                                low_vul_number += 1

                            try:
                                rule_num[vul.get('rule_name')] += 1
                            except KeyError:
                                rule_num[vul.get('rule_name')] = 1

                    else:
                        logger.debug('[REPORT] Empty result in {0}'.format(data_file))

        time_range = sorted_dict(time_range)

    return render_template(template_name_or_list='report_my.html',
                           time_start=time_start,
                           time_end=time_end,
                           total=len(data_lists),
                           total_files=total_files,
                           critical_vul_number=critical_vul_number,
                           high_vul_number=high_vul_number,
                           medium_vul_number=medium_vul_number,
                           low_vul_number=low_vul_number,
                           total_vul_number=total_vul_number,
                           rule_num=rule_num,
                           time_range=time_range)


@app.route('/', methods=['GET', 'POST'])
def summary():
    a_sid = request.args.get(key='sid')
    key = Config(level1="cobra", level2="secret_key").value
    if a_sid is None:
        return render_template(template_name_or_list='index.html',
                               key=key)

    status_url = 'http://{host}:{port}/api/status'.format(host=running_host, port=running_port)
    post_data = {
        'key': key,
        'sid': a_sid,
    }
    headers = {
        "Content-Type": "application/json",
    }
    r = requests.post(url=status_url, headers=headers, data=json.dumps(post_data))
    try:
        scan_status = json.loads(r.text)
    except ValueError as e:
        return render_template(template_name_or_list='error.html',
                               msg='Check scan status failed: {0}'.format(e))

    if scan_status.get('code') != 1001:
        return render_template(template_name_or_list='error.html',
                               msg=scan_status.get('msg'))
    else:
        if scan_status.get('result').get('status') == 'running':
            still_running = scan_status.get('result').get('still_running')
            for s_sid, target_str in still_running.items():
                target, branch = split_branch(target_str)
                still_running[s_sid] = {'target': target,
                                        'branch': branch}
        else:
            still_running = dict()

        scan_status_file = os.path.join(running_path, '{sid}_status'.format(sid=a_sid))

        scan_list = Running(a_sid).list()

        start_time = os.path.getctime(filename=scan_status_file)
        start_time = time.localtime(start_time)
        start_time = time.strftime('%Y-%m-%d %H:%M:%S', start_time)

        total_targets_number = scan_status.get('result').get('total_target_num')
        not_finished_number = scan_status.get('result').get('not_finished')

        total_vul_number, critical_vul_number, high_vul_number, medium_vul_number, low_vul_number = 0, 0, 0, 0, 0
        rule_num = dict()
        rules = dict()
        targets = list()

        for s_sid, target_str in scan_list.get('sids').items():
            if s_sid not in still_running:
                target_info = dict()

                # 分割项目地址与分支，默认 master
                target, branch = split_branch(target_str)

                target_info.update({
                    'sid': s_sid,
                    'target': target,
                    'branch': branch,
                })
                s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
                with open(s_sid_file, 'r') as f:
                    s_sid_data = json.load(f)
                    if s_sid_data.get('code') != 1001:
                        continue
                    else:
                        s_sid_data = s_sid_data.get('result')
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
                        rule_num[vul.get('rule_name')] += 1
                    except KeyError:
                        rule_num[vul.get('rule_name')] = 1

                    rules[vul.get('id')] = vul.get('rule_name')

        return render_template(template_name_or_list='summary.html',
                               total_targets_number=total_targets_number,
                               not_finished_number=not_finished_number,
                               start_time=start_time,
                               targets=targets,
                               a_sid=a_sid,
                               total_vul_number=total_vul_number,
                               critical_vul_number=critical_vul_number,
                               high_vul_number=high_vul_number,
                               medium_vul_number=medium_vul_number,
                               low_vul_number=low_vul_number,
                               rule_num=rule_num,
                               rules=rules,
                               running=still_running, )


def key_verify(data):
    key = Config(level1="cobra", level2="secret_key").value
    _key = data.get("key")

    if _key == key:
        return True
    elif not _key or _key == "":
        return {"code": 1002, "msg": "Key cannot be empty."}
    elif not _key == key:
        return {"code": 4002, "msg": "Key verify failed."}
    else:
        return {"code": 4002, "msg": "Unknown key verify error."}


def is_text(fn):
    msg = subprocess.Popen(['file', fn], stdout=subprocess.PIPE).communicate()[0]
    return 'text' in msg.decode('utf-8')


def guess_type(fn):
    import mimetypes
    extension = mimetypes.guess_type(fn)[0]
    if extension:
        """text/x-python or text/x-java-source"""
        # extension = extension.split('/')[1]
        extension = extension.replace('-source', '')
    else:
        extension = fn.split('/')[-1].split('.')[-1]

    custom_ext = {
        'html': 'htmlmixed',
        'md': 'markdown',
    }
    if custom_ext.get(extension) is not None:
        extension = custom_ext.get(extension)

    return extension.lower()


def search_rule(sid, rule_id):
    """
    Search specific rule name in scan data.
    :param sid: scan data id
    :param rule_id: a list of rule name
    :return: {rule_name1: num1, rule_name2: num2}
    """
    scan_data_file = os.path.join(running_path, '{sid}_data'.format(sid=sid))
    search_result = dict.fromkeys(rule_id, 0)
    if not os.path.exists(scan_data_file):
        return search_result

    with open(scan_data_file, 'r') as f:
        scan_data = json.load(f)

    if scan_data.get('code') == 1001 and len(scan_data.get('result').get('vulnerabilities')) > 0:
        for vul in scan_data.get('result').get('vulnerabilities'):
            if vul.get('id') in rule_id:
                search_result[vul.get('id')] += 1
        return search_result
    else:
        return search_result


def sorted_dict(adict):
    adict = adict.items()
    return sorted(adict)


def start(host, port, debug):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    api = Blueprint("api", __name__)
    resource = Api(api)

    resource.add_resource(AddJob, '/api/add')
    resource.add_resource(JobStatus, '/api/status')
    resource.add_resource(FileUpload, '/api/upload')
    resource.add_resource(ResultData, '/api/list')
    resource.add_resource(ResultDetail, '/api/detail')
    resource.add_resource(Search, '/api/search')
    resource.add_resource(GetMemeber, '/api/members')

    app.register_blueprint(api)

    # consumer
    threads = []
    for i in range(5):
        threads.append(threading.Thread(target=consumer, args=()))

    for i in threads:
        i.setDaemon(daemonic=True)
        i.start()

    try:
        global running_port, running_host
        running_host = host if host != '0.0.0.0' else '127.0.0.1'
        running_port = port
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error as v:
        if v.errno == errno.EACCES:
            logger.critical('[{err}] must root permission for start API Server!'.format(err=v.strerror))
            exit()
        else:
            logger.critical('{msg}'.format(msg=v.strerror))

    logger.info('API Server start success')
