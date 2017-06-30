import socket
import errno
from flask import Flask
from flask_restful import Api
from cobra.app.api.controller import *
from cobra.utils.log import logger


def start(host, port, debug):
    logger.info('Start {host}:{port}'.format(host=host, port=port))
    app = Flask(__name__)
    api = Api(app)
    api.add_resource(Scan, '/scan')
    api.add_resource(Status, '/status/<string:job_id>')
    try:
        app.run(debug=debug, host=host, port=int(port), threaded=True, processes=1)
    except socket.error, v:
        if v[0] == errno.EACCES:
            logger.critical('must sudo permission for start RESTful server!')
            exit()
        else:
            logger.critical('{msg}'.format(msg=v[1]))

    logger.info('RESTful server start success')

from flask import request
from flask_restful import Resource


class Scan(Resource):
    def put(self):
        token = request.form['token']
        return {'hello': 'world'}


class Status(Resource):
    def get(self, job_id):
        return {job_id: 'running'}



# -*- coding: utf-8 -*-

"""
    controller.front.api
    ~~~~~~~~~~~~~~~~~~~~

    External API interface implementation
    :doc:       http://cobra-docs.readthedocs.io/en/latest/API

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import traceback
from cobra.utils import config, common
from flask import request, jsonify
from werkzeug.utils import secure_filename
from cobra.app import db, web
from cobra.app.models import CobraResults, CobraRules, CobraProjects, CobraVuls, CobraAuth, CobraTaskInfo
from cobra.engine import scan
from cobra.utils.log import logging

logging = logging.getLogger(__name__)

# API base path
API_URL = '/api'


@web.route(API_URL + '/add', methods=['POST'])
def add_task():
    """
    Create a scan task
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
    new_version = data.get('new_version', '')
    old_version = data.get('old_version', '')

    # one-click scan for manage projects
    project_id = data.get('project_id')
    if project_id is not None:
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
    """
    Query the scan task status
    :return:
    """
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
    # project_id
    project_info = CobraProjects.query.filter_by(repository=c.target).first()
    if project_info:
        report = 'http://' + domain + '/report/' + str(project_info.id)
    else:
        report = 'http://' + domain
    result = {
        'status': status_text,
        'text': 'Success',
        'report': report,
        'allow_deploy': True
    }
    return jsonify(status=1001, result=result)


@web.route(API_URL + '/upload', methods=['POST'])
def upload_file():
    """
    Scan by uploading compressed files
    :return:
    """
    if 'file' not in request.files:
        return jsonify(code=1002, result="File can't empty!")
    file_instance = request.files['file']
    if file_instance.filename == '':
        return jsonify(code=1002, result="File name can't empty!")
    if file_instance and common.allowed_file(file_instance.filename):
        filename = secure_filename(file_instance.filename)
        file_instance.save(os.path.join(os.path.join(config.Config('upload', 'directory').value, 'uploads'), filename))
        # Start scan
        code, result = scan.Scan(filename).compress()
        return jsonify(code=code, result=result)
    else:
        return jsonify(code=1002, result="This extension can't support!")


@web.route(API_URL + '/queue', methods=['POST'])
def queue():
    from cobra.utils.queue import Queue
    """
    Pushed to a third-party vulnerability management platform
    Start the queue first
        celery -A daemon worker --loglevel=info

    :return:
    """
    # Configure the project ID and the vulnerability ID
    project_id = request.json.get('project_id')
    rule_id = request.json.get('rule_id')
    if project_id is None or rule_id is None:
        return jsonify(code=1002, result='Project ID and Rule ID can\'t empty!')

    # Project Info
    project_info = CobraProjects.query.filter_by(id=project_id).first()

    # Unpunched vulnerability and rule information
    result_all = db.session().query(CobraRules, CobraResults).join(CobraResults, CobraResults.rule_id == CobraRules.id).filter(
        CobraResults.project_id == project_id,
        CobraResults.status == 0,
        CobraResults.rule_id == rule_id
    ).all()

    if len(result_all) == 0:
        return jsonify(code=1001, result="There are no unpacked vulnerabilities")

    # Dealing with vulnerabilities
    for index, (rule, result) in enumerate(result_all):
        try:
            # Query the vulnerability type information
            vul_info = CobraVuls.query.filter(CobraVuls.id == rule.vul_id).first()
            # Pushed to a third-party vulnerability management platform
            q = Queue(project_info.name, vul_info.name, vul_info.third_v_id, result.file, result.line, result.code, result.id)
            q.push()
        except:
            print(traceback.print_exc())
    return jsonify(code=1001, result="Successfully pushed {0} vulnerabilities to a third-party vulnerability management platform".format(len(result_all)))


# -*- coding: utf-8 -*-

"""
    controller.front.route
    ~~~~~~~~~~~~~~~~~~~~~~

    Implements the route for controller

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
import os
from cobra.pickup.git import Git
from cobra.utils import common, config, const
from flask import jsonify, render_template, request, abort, session
from sqlalchemy import and_, func
from cobra.app import db, web
from cobra.app.models import CobraTaskInfo, CobraProjects, CobraResults, CobraRules, CobraVuls, CobraExt, CobraLanguages


@web.route('/', methods=['GET'])
@web.route('/index', methods=['GET'])
def homepage():
    tasks = CobraTaskInfo.query.order_by(CobraTaskInfo.id.desc()).limit(10).all()
    recently_tasks = []
    for task in tasks:
        recently_tasks.append({
            'id': task.id,
            'target': task.target,
            'branch': task.branch,
            'scan_way': task.scan_way
        })
    data = {
        'key': common.md5('CobraAuthKey'),
        'extensions': config.Config('upload', 'extensions').value,
        'recently_tasks': recently_tasks
    }
    return render_template('index.html', data=data)


@web.route('/report/<int:project_id>', methods=['GET'])
def report(project_id):
    is_login = session.get('is_login') and session.get('is_login') is True
    search_task_id = request.args.get("search_task", "")
    search_task_id = None if search_task_id == "all" or search_task_id == "" else search_task_id
    project_info = CobraProjects.query.filter(CobraProjects.id == project_id).first()
    if project_info is None:
        abort(404)

    # Use the project's latest task if not have task id
    if search_task_id is None:
        task_info = CobraTaskInfo.query.filter(
            CobraTaskInfo.target == project_info.repository
        ).order_by(CobraTaskInfo.id.desc()).first()
    else:
        task_info = CobraTaskInfo.query.filter(CobraTaskInfo.id == search_task_id).first()

    if task_info is None:
        abort(404)

    code_number = u"Statistics..." \
        if task_info.code_number is None or task_info.code_number == 0 \
        else common.convert_number(task_info.code_number)

    # timestamp->datetime
    time_start = time.strftime("%H:%M:%S", time.localtime(task_info.time_start))
    time_end = time.strftime("%H:%M:%S", time.localtime(task_info.time_end))

    # tasks
    tasks = CobraTaskInfo.query.filter_by(target=project_info.repository).order_by(CobraTaskInfo.updated_at.desc()).all()

    # get project's all result if not have task id
    if search_task_id is None:
        # Default task id
        search_task_id = tasks[0].id

        # vulnerability count
        scan_results_number = CobraResults.query.filter(CobraResults.project_id == project_id).count()
        # scan_results_number = db.session.query(func.count()).filter(CobraResults.project_id == project_id)
        # Not fixed vulnerability count
        unrepair_results_number = CobraResults.query.filter(
            CobraResults.project_id == project_id, CobraResults.status < 2
        ).count()
        # Fixed vulnerability count
        repaired_results_number = CobraResults.query.filter(
            CobraResults.project_id == project_id, CobraResults.status == 2
        ).count()
        # Not fixed vulnerability types
        showed_vul_type = db.session.query(
            func.count().label("showed_vul_number"), CobraVuls.name, CobraVuls.id
        ).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraVuls.name, CobraVuls.id).all()
        # Not fixed rules types
        showed_rule_type = db.session.query(CobraRules.description, CobraRules.id).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraRules.id).all()
        # Fixed vulnerability count group by level
        showed_repaired_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status == 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
        # Not fixed vulnerability count group by level
        showed_unrepair_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
        # Total vulnerability count group by level
        showed_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
    else:
        # Select the task's result if have special task id
        # Total vulnerability count
        scan_results_number = CobraResults.query.filter(
            CobraResults.task_id == search_task_id
        ).count()
        # Not fixed vulnerability count
        unrepair_results_number = CobraResults.query.filter(
            CobraResults.task_id == search_task_id, CobraResults.status < 2
        ).count()
        # Fixed vulnerability count
        repaired_results_number = CobraResults.query.filter(
            CobraResults.task_id == search_task_id, CobraResults.status == 2
        ).count()
        # Not fixed vulnerability types
        showed_vul_type = db.session.query(
            func.count().label("showed_vul_number"), CobraVuls.name, CobraVuls.id
        ).filter(
            and_(
                CobraResults.task_id == search_task_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraVuls.name, CobraVuls.id).all()
        # Not fixed vulnerability rules types
        showed_rule_type = db.session.query(CobraRules.description, CobraRules.id).filter(
            and_(
                CobraResults.task_id == search_task_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraRules.id).all()
        # Fixed vulnerability count group by level
        showed_repaired_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.task_id == search_task_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status == 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
        # Not fixed vulnerability count group by level
        showed_unrepair_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.task_id == search_task_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
        # Total vulnerability count group by level
        showed_level_number = db.session.query(
            func.count().label('vuln_number'), CobraRules.level
        ).filter(
            and_(
                CobraResults.task_id == search_task_id,
                CobraResults.rule_id == CobraRules.id,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()

    # For frontpage filter
    select_vul_type = list()
    # Every vulnerability count
    chart_vuls_number = list()
    for r in showed_vul_type:
        select_vul_type.append([r[1], r[2]])
        chart_vuls_number.append({"vuls_name": r[1], "vuls_number": r[0]})
    select_rule_type = list()
    for r in showed_rule_type:
        select_rule_type.append([r[0], r[1]])
    # Statistic every vulnerability status level description
    # 1-low， 2-medium， 3-high， other-undefined
    # Total number
    low_level_number = medium_level_number = high_level_number = unknown_level_number = 0
    for every_level in showed_level_number:
        if every_level[1] == 1:
            low_level_number = every_level[0]
        elif every_level[1] == 2:
            medium_level_number = every_level[0]
        elif every_level[1] == 3:
            high_level_number = every_level[0]
        else:
            unknown_level_number = every_level[0]
    # Fixed number
    repaired_low_level_number = repaired_medium_level_number = repaired_high_level_number = repaired_unknown_level_number = 0
    for every_level in showed_repaired_level_number:
        if every_level[1] == 1:
            repaired_low_level_number = every_level[0]
        elif every_level[1] == 2:
            repaired_medium_level_number = every_level[0]
        elif every_level[1] == 3:
            repaired_high_level_number = every_level[0]
        else:
            repaired_unknown_level_number = every_level[0]
    # Not fixed number
    unrepair_low_level_number = unrepair_medium_level_number = unrepair_high_level_number = unrepair_unknown_level_number = 0
    for every_level in showed_unrepair_level_number:
        if every_level[1] == 1:
            unrepair_low_level_number = every_level[0]
        elif every_level[1] == 2:
            unrepair_medium_level_number = every_level[0]
        elif every_level[1] == 3:
            unrepair_high_level_number = every_level[0]
        else:
            unrepair_unknown_level_number = every_level[0]

    # Status description
    vuls_status = [
        {"status": "All", "value": 0},
        {"status": "Fixed", "value": 1},
        {"status": "Not fixed", "value": 2},
        {"status": "Other", "value": 3},
    ]

    # detect project Cobra configuration file
    if project_info.repository[0] == '/':
        project_directory = project_info.repository
    else:
        project_directory = Git(project_info.repository).repo_directory
    cobra_properties = config.properties(os.path.join(project_directory, 'cobra'))
    need_scan = True
    if 'scan' in cobra_properties:
        need_scan = common.to_bool(cobra_properties['scan'])

    data = {
        "project_id": project_id,
        "task_id": search_task_id,
        "select_vul_type": select_vul_type,
        "select_rule_type": select_rule_type,
        "chart_vuls_number": chart_vuls_number,
        "task_info": task_info,
        "project_info": project_info,
        "code_number": code_number,
        "file_count": common.convert_number(task_info.file_count),
        "tasks": tasks,
        "vuls_status": vuls_status,
        'need_scan': need_scan,
        "task_time": {
            "time_start": time_start,
            "time_end": time_end,
            "time_consume": common.convert_time(task_info.time_consume)
        },
        "vuls_number": {
            "unrepair": {
                "low": unrepair_low_level_number,
                "medium": unrepair_medium_level_number,
                "high": unrepair_high_level_number,
                "unknown": unrepair_unknown_level_number,
            },
            "repaired": {
                "low": repaired_low_level_number,
                "medium": repaired_medium_level_number,
                "high": repaired_high_level_number,
                "unknown": repaired_unknown_level_number,
            },
            "total_number": {
                "low": low_level_number,
                "medium": medium_level_number,
                "high": high_level_number,
                "unknown": unknown_level_number
            },
            "result_number": {
                "scan_result_number": scan_results_number,
                "repaired_result_number": repaired_results_number,
                "unrepair_result_number": unrepair_results_number,
            }
        },
        'is_login': is_login
    }
    return render_template('report.html', data=data)


@web.route('/list', methods=['POST'])
def vulnerabilities_list():
    project_id = request.form.get("project_id", None)
    search_vul_id = request.form.get("search_vul_type", None)
    search_rule_id = request.form.get("search_rule", None)
    search_level = request.form.get("search_level", None)
    search_task_id = request.form.get("search_task", "")
    search_task_id = None if search_task_id == "all" or search_task_id == "" else search_task_id
    # Default page 1
    try:
        page = int(request.form.get("page", 1))
    except ValueError:
        page = 1
    # 0 - all, 1 - repaired, 2 - unrepair, 3 - others
    search_status_type = request.form.get("search_status", 2)
    # status: 0 - all, 1 - repaired, 2 - unrepair, 3 - others
    if search_task_id is None:
        filter_group = (
            CobraResults.project_id == project_id,
            CobraResults.rule_id == CobraRules.id,
            CobraVuls.id == CobraRules.vul_id,
        )
    else:
        filter_group = (
            CobraResults.task_id == search_task_id,
            CobraResults.rule_id == CobraRules.id,
            CobraVuls.id == CobraRules.vul_id,
        )

    if search_status_type == "1":
        filter_group += (CobraResults.status == 2,)
    elif search_status_type == "2":
        filter_group += (CobraResults.status < 2,)
    elif search_status_type == "3":
        filter_group += (CobraResults.status == 1,)

    if search_vul_id is not None and search_vul_id != "all":
        filter_group += (CobraVuls.id == search_vul_id,)
    if search_rule_id is not None and search_rule_id != "all":
        filter_group += (CobraRules.id == search_rule_id,)
    if search_level is not None and search_level != "all":
        filter_group += (CobraRules.level == search_level,)

    all_scan_results = db.session.query(
        CobraResults.id, CobraResults.file, CobraResults.line, CobraResults.code,
        CobraRules.description, CobraRules.level, CobraRules.regex_location,
        CobraRules.regex_repair, CobraRules.repair, CobraVuls.name,
        CobraResults.rule_id, CobraResults.status
    ).filter(
        *filter_group
    )

    # Single page size
    page_size = 15
    total_number = all_scan_results.all()
    pagination = {
        'page': page,
        'total': len(total_number),
        'per_page': page_size
    }
    total_pages = len(total_number) / page_size + 1
    all_scan_results = all_scan_results.limit(page_size).offset((page - 1) * page_size).all()

    vulnerabilities = list()
    map_level = ["Undefined", "Low", "Medium", "High"]
    map_color = ["low", "low", "medium", "high"]
    for result in all_scan_results:
        data_dict = dict()
        data_dict['id'] = result[0]
        data_dict["file"] = result[1]
        data_dict["file_short"] = common.path_to_file(result[1])
        data_dict["line"] = result[2]
        data_dict["code"] = result[3]
        data_dict["rule"] = result[4]
        data_dict["level"] = map_level[result[5]]
        data_dict["color"] = map_color[result[5]]
        data_dict["repair"] = result[8]
        data_dict["v_name"] = result[9]
        data_dict['verify'] = ''
        data_dict['rule_id'] = result[10]
        if result[11] == 2:
            status_class = u'fixed'
        elif result[11] == 1:
            status_class = u'not_fixed'
        else:
            status_class = u'not_fixed'
        data_dict["status"] = result[11]
        data_dict["status_class"] = status_class
        vulnerabilities.append(data_dict)
    current_url = request.url.replace("&page={}".format(page), "").replace("page={}".format(page), "")
    if "?" not in current_url:
        current_url += "?"
    return_data = {
        "current_page": page,
        "total_pages": total_pages,
        "search_status_type": search_status_type,
        "filter_vul_number": len(total_number),
        "current_url": current_url,
        "pagination": pagination,
        'vulnerabilities': vulnerabilities,
    }
    return jsonify(status_code=1001, message='success', data=return_data)


@web.route('/detail', methods=['POST'])
def vulnerabilities_detail():
    v_id = request.form.get("id", None)
    # query result/rules/vulnerabilities
    v_detail = CobraResults.query.filter_by(id=v_id).first()
    rule_info = CobraRules.query.filter_by(id=v_detail.rule_id).first()
    language_info = CobraLanguages.query.filter(CobraLanguages.id == rule_info.language).first()
    language = language_info.language
    vulnerabilities_description = CobraVuls.query.filter_by(id=rule_info.vul_id).first()

    if rule_info.author.strip() == '':
        rule_info.author = 'Undefined'

    # get code content
    project = CobraProjects.query.filter_by(id=v_detail.project_id).first()
    if project.repository[0] == '/':
        # upload directory
        project_code_path = project.repository
    else:
        # git
        project_path_split = project.repository.replace('.git', '').split('/')
        project_path = os.path.join(project_path_split[3], project_path_split[4])
        upload = os.path.join(config.Config('upload', 'directory').value, 'versions')
        project_code_path = os.path.join(upload, project_path)
    if v_detail.file[0] == '/':
        v_detail.file = v_detail.file[1:]
    file_path = os.path.join(project_code_path, v_detail.file)

    # https://codemirror.net/mode/clike/index.html
    mode_mime = {
        'javascript': 'javascript',
        'php': 'php',
        'python': 'python',
        'lua': 'lua',
        'ruby': 'ruby',
        'perl': 'perl',
        'go': 'go',
        'cmake': 'cmake',
        'html': 'htmlmixed',
        'jsp': 'htmlmixed',
        'xml': 'xml',
        'yaml': 'yaml',
        'css': 'css',
        'markdown': 'markdown',
        'shell': 'shell',
        'sql': 'sql',
        'c': 'text/x-csrc',
        'c++': 'text/x-c++src',
        'java': 'text/x-java',
        'c#': 'text/x-csharp',
        'objective-c': 'text/x-objectivec',
        'scale': 'text/x-scale',
        'shader': 'text/x-vertex',
        'squirrel': 'text/x-squirrel',
        'kotlin': 'text/x-kotlin',
        'ceylon': 'text/ceylon'
    }
    if language.lower() in mode_mime:
        mode = mode_mime[language.lower()]
    else:
        mode = 'htmlmixed'
        if '.' in file_path:
            ext = file_path.split('.')[-1:][0]
            if ext.lower() in mode_mime:
                mode = mode_mime[ext.lower()]

    if os.path.isfile(file_path) is not True:
        code_content = '// File does not exist'
        line_trigger = 1
        line_start = 1
        c_author = 'Not support'
        c_time = 'Not support'
        c_ret = False
    else:
        # get committer
        c_ret, c_author, c_time = Git.committer(v_detail.file, project_code_path, v_detail.line)
        if c_ret is not True:
            c_author = 'Not support'
            c_time = 'Not support'

        # get code content
        code_content = ''
        fp = open(file_path, 'r')
        block_lines = 50
        block_start = 0
        if v_detail.line < block_lines:
            block_end = v_detail.line + block_lines
        else:
            block_end = v_detail.line + block_lines
        for i, line in enumerate(fp):
            if i == 0 and len(line) > 1024:
                code_content = '// Compressed file preview is not supported'
                break
            else:
                if block_start <= i <= block_end:
                    code_content = code_content + line
        fp.close()

        line_trigger = v_detail.line - block_start
        line_start = block_start + 1

        try:
            jsonify(data=code_content)
        except Exception as e:
            code_content = '// The file encoding type is not supported'
            line_trigger = 1
            line_start = 1

    return_data = {
        'detail': {
            'id': v_detail.id,
            'file': v_detail.file,
            'line_trigger': line_trigger,
            'line_start': line_start,
            'code': code_content,
            'c_ret': c_ret,
            'c_author': c_author,
            'c_time': c_time,
            'mode': mode,
            'repair': const.Vulnerabilities(v_detail.repair).repair_description(),
            'status': const.Vulnerabilities(v_detail.status).status_description(),
            'created': str(v_detail.created_at),
            'updated': str(v_detail.updated_at)
        },
        'rule': {
            'id': rule_info.id,
            'language': language,
            'description': rule_info.description,
            'repair': rule_info.repair,
            'author': rule_info.author,
            'level': const.Vulnerabilities(rule_info.level).level_description(),
            'status': rule_info.status,
            'created': str(rule_info.created_at),
            'updated': str(rule_info.updated_at)
        },
        'description': {
            'id': vulnerabilities_description.id,
            'name': vulnerabilities_description.name,
            'description': vulnerabilities_description.description,
            'repair': vulnerabilities_description.repair,
            'third_v_id': vulnerabilities_description.third_v_id
        }
    }
    return jsonify(status_code=1001, message='success', data=return_data)


@web.route('/ext/<int:task_id>', methods=['GET'])
def ext_statistic(task_id):
    # Ext Amount Statistic
    exts = CobraExt.query.filter_by(task_id=task_id).all()
    exts_result = []
    for ext in exts:
        if ext.ext == '':
            name = '[No extension]'
        else:
            name = ext.ext
        exts_result.append({
            'value': ext.amount,
            'name': name,
            'path': ext.ext
        })
    return jsonify(code=1001, result=exts_result)


@web.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
