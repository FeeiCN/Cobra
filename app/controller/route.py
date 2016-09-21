# -*- coding: utf-8 -*-

"""
    controller.route
    ~~~~~~~~~~~~~~~~

    Implements the route for controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time

from utils import common, config
from flask import jsonify, render_template, request, abort
from flask_paginate import Pagination
from sqlalchemy import and_
from sqlalchemy.sql.functions import count

from engine import detection
from app import web, db, CobraTaskInfo, CobraProjects, CobraResults, CobraRules, CobraVuls, CobraExt


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
    # 获取筛选数据
    search_vul_type = request.args.get("search_vul_type", None)
    search_rule = request.args.get("search_rule", None)
    search_level = request.args.get("search_level", None)
    search_task = request.args.get("search_task", None)
    if search_task == 'all':
        search_task = None

    # 当前页码,默认为第一页
    page = int(request.args.get("page", 1))

    # 检测 task id 是否存在
    project_info = CobraProjects.query.filter_by(id=project_id).first()
    if not project_info:
        abort(404)
    if search_task is None:
        task_info = CobraTaskInfo.query.filter_by(target=project_info.repository).order_by(CobraTaskInfo.id.desc()).first()
    else:
        task_info = CobraTaskInfo.query.filter_by(id=search_task).first()
        if task_info is None:
            abort(404)

    # 获取task的信息
    repository = task_info.target
    task_created_at = task_info.created_at
    time_consume = task_info.time_consume
    time_start = task_info.time_start
    time_end = task_info.time_end
    files = task_info.file_count
    code_number = task_info.code_number
    if code_number is None or code_number == 0:
        code_number = u"统计中..."
    else:
        code_number = common.convert_number(code_number)

    # 把时间戳转换成datetime
    time_start = time.strftime("%H:%M:%S", time.localtime(time_start))
    time_end = time.strftime("%H:%M:%S", time.localtime(time_end))

    # 获取project信息
    if project_info is None:
        project_name = repository
        project_id = 0  # add l4yn3
        author = 'Anonymous'
        project_description = 'Compress Project'
        project_framework = 'Unknown Framework'
        project_url = 'Unknown URL'
    else:
        project_name = project_info.name
        project_id = project_info.id
        author = project_info.author
        project_description = project_info.remark
        project_framework = project_info.framework
        project_url = project_info.url

    if search_task is None:
        # 获取漏洞总数
        scan_results = CobraResults.query.filter(CobraResults.project_id == project_id).count()
        # 待修复漏洞总数
        unrepair_results = CobraResults.query.filter(CobraResults.project_id == project_id, CobraResults.status < 2).count()
        # 已修复漏洞总数
        repaired_results = CobraResults.query.filter(CobraResults.project_id == project_id, CobraResults.status == 2).count()

        # 获取出现的漏洞类型
        res = db.session.query(count().label("vul_number"), CobraVuls.name, CobraVuls.id).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraVuls.name, CobraVuls.id).all()
    else:
        # 获取漏洞总数量
        scan_results = CobraResults.query.filter(CobraResults.task_id == search_task).count()
        # 待修复漏洞总数
        unrepair_results = CobraResults.query.filter(CobraResults.task_id == search_task, CobraResults.status < 2).count()
        # 已修复漏洞总数
        repaired_results = CobraResults.query.filter(CobraResults.task_id == search_task, CobraResults.status == 2).count()

        # 获取出现的漏洞类型
        res = db.session.query(count().label("vul_number"), CobraVuls.name, CobraVuls.id).filter(
            and_(
                CobraResults.task_id == search_task,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraVuls.name, CobraVuls.id).all()
    total_vul_count = scan_results
    total_vul_count_unrepair = unrepair_results
    total_vul_count_repaired = repaired_results

    # 提供给筛选列表
    select_vul_type = list()
    # 存下每种漏洞数量
    chart_vuls_number = list()
    for r in res:
        select_vul_type.append([r[1], r[2]])
        chart_vuls_number.append({"vuls_name": r[1], "vuls_number": r[0]})

    # 获取触发的规则类型
    if search_task is None:
        res = db.session.query(CobraRules.description, CobraRules.id).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraRules.id).all()
    else:
        res = db.session.query(CobraRules.description, CobraRules.id).filter(
            and_(
                CobraResults.task_id == search_task,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id
            )
        ).group_by(CobraRules.id).all()
    select_rule_type = list()
    for r in res:
        select_rule_type.append([r[0], r[1]])

    # 检索不同等级的漏洞数量
    if search_task is None:
        res = db.session.query(count().label('vuln_number'), CobraRules.level, CobraResults.status).filter(
            and_(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
    else:
        res = db.session.query(count().label('vuln_number'), CobraRules.level, CobraResults.status).filter(
            and_(
                CobraResults.task_id == search_task,
                CobraResults.rule_id == CobraRules.id,
                CobraResults.status < 2,
                CobraVuls.id == CobraRules.vul_id,
            )
        ).group_by(CobraRules.level).all()
    low_amount = medium_amount = high_amount = unknown_amount = 0
    for every_level in res:
        """
        低危:1
        中危:2
        高危:3
        未定义:其他值
        """
        if every_level[1] == 1:
            low_amount = every_level[0]
        elif every_level[1] == 2:
            medium_amount = every_level[0]
        elif every_level[1] == 3:
            high_amount = every_level[0]
        else:
            unknown_amount = every_level[0]

    # 检索全部的漏洞信息
    if search_task is None:
        filter_group = (
            CobraResults.project_id == project_id,
            CobraResults.rule_id == CobraRules.id,
            CobraResults.status < 2,
            CobraVuls.id == CobraRules.vul_id,
        )
    else:
        filter_group = (
            CobraResults.task_id == search_task,
            CobraResults.rule_id == CobraRules.id,
            CobraResults.status < 2,
            CobraVuls.id == CobraRules.vul_id,
        )

    # 根据传入的筛选条件添加SQL的条件
    if search_vul_type is not None and search_vul_type != "all":
        filter_group += (CobraVuls.id == search_vul_type,)
    if search_rule is not None and search_rule != "all":
        filter_group += (CobraRules.id == search_rule,)
    if search_level is not None and search_level != "all":
        filter_group += (CobraRules.level == search_level,)

    # 构建SQL语句
    all_scan_results = db.session.query(
        CobraResults.file,
        CobraResults.line,
        CobraResults.code,
        CobraRules.description,
        CobraRules.level,
        CobraRules.regex_location,
        CobraRules.regex_repair,
        CobraRules.repair,
        CobraVuls.name,
        CobraResults.rule_id
    ).filter(
        *filter_group
    )
    page_size = 5
    total_number = all_scan_results.all()
    total_pages = len(total_number) / page_size + 1
    all_scan_results = all_scan_results.limit(page_size).offset((page - 1) * page_size).all()

    # 处理漏洞信息
    vulnerabilities = list()
    map_level = ["未定义", "低危", "中危", "高危"]
    map_color = ["#555", "black", "orange", "red"]
    current_url = ''
    for result in all_scan_results:

        # 生成data数据
        data_dict = dict()
        data_dict["file"] = result[0]
        data_dict["line"] = result[1]
        data_dict["code"] = result[2]
        data_dict["rule"] = result[3]
        data_dict["level"] = map_level[result[4]]
        data_dict["color"] = map_color[result[4]]
        data_dict["repair"] = result[7]
        data_dict['verify'] = ''
        data_dict['rule_id'] = result[9]

        if project_framework != '':
            for rule in detection.Detection().rules:
                if rule['name'] == project_framework:
                    if 'public' in rule:
                        if result.file[:len(rule['public'])] == rule['public']:
                            data_dict['verify'] = project_url + result.file.replace(rule['public'], '')

        # 检索vulnerabilities中是否存在vul_type的类别
        # 如果存在就添加到对应的data字典中
        # 否则就新建一下
        found = False
        for v in vulnerabilities:
            if v["vul_type"] == result[-1]:
                # 直接添加
                v["data"].append(data_dict)
                # 修改标志
                found = True
                break
        # 没有找到
        if not found:
            temp_dict = dict(vul_type=result[-1], data=list())
            temp_dict["data"].append(data_dict)
            vulnerabilities.append(temp_dict)

        current_url = request.url.replace("&page={}".format(page), "").replace("page={}".format(page), "")
        if "?" not in current_url:
            current_url += "?"

    # 设置分页
    pagination = Pagination(page=page, total=len(total_number), per_page=page_size, bs_version=3)

    # 任务信息
    tasks = CobraTaskInfo.query.filter_by(target=repository).order_by(CobraTaskInfo.updated_at.desc()).all()

    data = {
        'id': int(project_id),
        'project_name': project_name,
        'project_id': project_id,
        'project_repository': repository,
        'project_description': project_description,
        'project_url': project_url,
        'project_framework': project_framework,
        'author': author,
        'task_created_at': task_created_at,
        'time_consume': common.convert_time(time_consume),
        'time_start': time_start,
        'time_end': time_end,
        'files': common.convert_number(files),
        'code_number': code_number,
        'vul_count': common.convert_number(total_vul_count),
        'vul_count_unrepair': common.convert_number(total_vul_count_unrepair),
        'vul_count_repaired': common.convert_number(total_vul_count_repaired),
        'vulnerabilities': vulnerabilities,
        "select_vul_type": select_vul_type,
        "select_rule_type": select_rule_type,
        "chart_vuls_number": chart_vuls_number,
        "current_page": page,
        "total_pages": total_pages,
        "filter_vul_number": len(total_number),
        "current_url": current_url,
        "pagination": pagination,
        'amount': {
            'h': high_amount,
            'm': medium_amount,
            'l': low_amount,
            'u': unknown_amount
        },
        'tasks': tasks
    }
    return render_template('report.html', data=data)


@web.route('/ext/<int:task_id>', methods=['GET'])
def ext_statistic(task_id):
    # Ext Amount Statistic
    exts = CobraExt.query.filter_by(task_id=task_id).all()
    exts_result = []
    for ext in exts:
        exts_result.append({
            'value': ext.amount,
            'name': ext.ext,
            'path': ext.ext
        })
    return jsonify(code=1001, result=exts_result)


@web.errorhandler(404)
def page_not_found(e):
    return render_template('404.html', error=e), 404
