# -*- coding: utf-8 -*-

"""
    backend.tasks
    ~~~~~~~~~~~~~

    Implements tasks controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import datetime

from flask import render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import ADMIN_URL
from app import web, db
from utils.validate import ValidateClass, login_required
from app.models import CobraTaskInfo, CobraProjects
from utils.common import convert_number, convert_time
from utils import config


# show all tasks
@web.route(ADMIN_URL + '/tasks/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/tasks/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/tasks/<int:page>/<keyword>', methods=['GET'])
@login_required
def tasks(page, keyword):
    if keyword != '0':
        filter_group = (CobraTaskInfo.target.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraTaskInfo.id > 0)
    per_page = 10
    all_tasks = CobraTaskInfo.query.filter(filter_group).order_by(CobraTaskInfo.id.desc()).limit(per_page).offset((page - 1) * per_page).all()

    total = CobraTaskInfo.query.filter(filter_group).count()

    tasks_dict = []
    for task in all_tasks:
        p = CobraProjects.query.with_entities(CobraProjects.id).filter(CobraProjects.repository == task.target).first()
        tasks_dict.append({
            'file_count': convert_number(task.file_count),
            'code_number': convert_number(task.code_number) if task.code_number != 0 else u"Statistic...",
            'time_start': datetime.datetime.fromtimestamp(task.time_start),
            'time_end': datetime.datetime.fromtimestamp(task.time_end),
            'time_consume': convert_time(task.time_consume),
            'updated_at': task.updated_at,
            'target': task.target,
            'id': task.id,
            'status': task.status,
            'pid': p.id,
            'report': 'http://' + config.Config('cobra', 'domain').value + '/report/' + str(p.id)
        })

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'tasks': tasks_dict,
        'page': page,
        'keyword': keyword
    }
    return render_template('backend/task/tasks.html', data=data)


# del the special task
@web.route(ADMIN_URL + '/tasks/del', methods=['POST'])
@login_required
def del_task():
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    task = CobraTaskInfo.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except SQLAlchemyError as e:
        print(e)
        return jsonify(code=4004, message='unknown error.')


@web.route(ADMIN_URL + "/tasks/search/<keyword>", methods=['GET'])
@login_required
def search_task(keyword):
    if keyword == "":
        return render_template("backend/task/tasks.html", data=None)
    else:
        all_tasks = CobraTaskInfo.query.filter(CobraTaskInfo.target.like("%{}%".format(keyword))).all()
        # 转换一些数据
        for task in all_tasks:
            task.file_count = convert_number(task.file_count)
            task.code_number = convert_number(task.code_number) if task.code_number != 0 else u"统计中..."
            task.time_start = datetime.datetime.fromtimestamp(task.time_start)
            task.time_end = datetime.datetime.fromtimestamp(task.time_end)
            task.time_consume = convert_time(task.time_consume)

        data = {
            'tasks': all_tasks,
            'keyword': keyword
        }
        return render_template('backend/task/tasks.html', data=data)
