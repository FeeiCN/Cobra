# -*- coding: utf-8 -*-

"""
    backend.tasks
    ~~~~~~~~~~~~~

    Implements tasks controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import datetime

from flask import render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraTaskInfo
from utils import config

__author__ = "lightless"
__email__ = "root@lightless.me"


# show all tasks
@web.route(ADMIN_URL + '/tasks/<int:page>', methods=['GET'])
@login_required
def tasks(page):
    per_page = 10
    tasks = CobraTaskInfo.query.order_by(CobraTaskInfo.id.desc()).limit(per_page).offset((page - 1) * per_page).all()

    # replace data
    for task in tasks:
        task.scan_way = "Full Scan" if task.scan_way == 1 else "Diff Scan"
        task.report = 'http://' + config.Config('cobra', 'domain').value + '/report/' + str(task.id)
    data = {
        'tasks': tasks,
    }
    return render_template('backend/task/tasks.html', data=data)


# del the special task
@web.route(ADMIN_URL + '/del_task', methods=['POST'])
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
        return jsonify(tag='success', msg='delete success.')
    except SQLAlchemyError as e:
        print(e)
        return jsonify(tag='danger', msg='unknown error.')


# edit the special task
@web.route(ADMIN_URL + '/edit_task/<int:task_id>', methods=['GET', 'POST'])
@login_required
def edit_task(task_id):
    if request.method == 'POST':

        # vc = ValidateClass(request, "branch", "scan_way", "new_version", "old_version", "target")
        # ret, msg = vc.check_args()
        # if not ret:
        #     return jsonify(tag="danger", msg=msg)
        # TODO: check new_version and old_version when scan_way == 2
        branch = request.form.get('branch')
        scan_way = request.form.get('scan_way')
        new_version = request.form.get('new_version')
        old_version = request.form.get('old_version')
        target = request.form.get('target')

        if not branch or branch == "":
            return jsonify(tag='danger', msg='branch can not be empty')
        if not scan_way or scan_way == "":
            return jsonify(tag='danger', msg='scan way can not be empty')
        if (scan_way == 2) and ((not new_version or new_version == "") or (not old_version or old_version == "")):
            return jsonify(tag='danger', msg='In diff scan mode, new version and old version can not be empty')
        if not target or target == "":
            return jsonify(tag='danger', msg='Target can not be empty.')

        task = CobraTaskInfo.query.filter_by(id=task_id).first()
        task.branch = branch
        task.scan_way = scan_way
        task.new_version = new_version
        task.old_version = old_version
        task.target = target
        task.updated_time = datetime.datetime.now()

        try:
            db.session.add(task)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except SQLAlchemyError as e:
            print(e)
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        task = CobraTaskInfo.query.filter_by(id=task_id).first()
        return render_template('backend/task/edit_task.html', data={
            'task': task,
        })
