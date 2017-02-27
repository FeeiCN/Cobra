# -*- coding: utf-8 -*-

"""
    backend.whitelist
    ~~~~~~~~~~~~~~~~~

    Implements whitelist controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
import datetime

from flask import jsonify, render_template, request

from . import ADMIN_URL
from app import web, db
from utils.validate import ValidateClass, login_required
from app.models import CobraWhiteList, CobraRules, CobraProjects


@web.route(ADMIN_URL + '/white-list/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/white-list/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/white-list/<int:page>/<keyword>', methods=['GET'])
@login_required
def white_list(page, keyword):
    if keyword != '0':
        filter_group = (CobraWhiteList.path.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraWhiteList.id > 0)
    per_page = 10
    whitelists = CobraWhiteList.query.filter(filter_group).order_by(CobraWhiteList.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraWhiteList.query.filter(filter_group).count()

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'whitelists': whitelists,
        'keyword': keyword,
        'page': page
    }
    return render_template('backend/white-list/white-list.html', data=data)


@web.route(ADMIN_URL + '/white-list/create/', methods=['GET', 'POST'])
@login_required
def add_white_list():
    if request.method == 'POST':
        vc = ValidateClass(request, "project", "rule", "path", "reason", 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if vc.vars.path[0] != '/':
            vc.vars.path = '/' + vc.vars.path
        whitelist = CobraWhiteList(vc.vars.project, vc.vars.rule, vc.vars.path, vc.vars.reason, vc.vars.status, current_time, current_time)
        try:
            db.session.add(whitelist)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except:
            return jsonify(code=4001, message='unknown error. Try again later?')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        data = {
            'title': 'Create white-list',
            'type': 'create',
            'rules': rules,
            'projects': projects,
            'whitelist': dict()
        }
        return render_template('backend/white-list/edit.html', data=data)


# del the special white list
@web.route(ADMIN_URL + '/white-list/delete', methods=['POST'])
@login_required
def delete_white_list():
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)

    whitelist = CobraWhiteList.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(whitelist)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except:
        return jsonify(code=4002, message='unknown error.')


@web.route(ADMIN_URL + '/vulnerability/delete/', methods=['POST'])
@login_required
def delete_vulnerability():
    vc = ValidateClass(request, 'vid')
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)
    from app.models import CobraResults

    try:
        vulnerability_ret = CobraResults.query.filter(CobraResults.id == vc.vars.vid).delete()
        if vulnerability_ret is not None:
            db.session.commit()
            return jsonify(code=1001, message='Deleted success!')
        else:
            return jsonify(code=4001, message='Not exist this vulnerability')
    except:
        return jsonify(code=4002, message="delete failed")


# edit the special white list
@web.route(ADMIN_URL + '/white-list/edit/<int:wid>', methods=['GET', 'POST'])
@login_required
def edit_white_list(wid):
    if request.method == 'POST':
        vc = ValidateClass(request, "project", "rule", "path", "reason", "status")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        white_list = CobraWhiteList.query.filter_by(id=wid).first()
        if not white_list:
            return jsonify(code=4001, message='wrong white-list')

        white_list.project_id = vc.vars.project
        white_list.rule_id = vc.vars.rule
        white_list.path = vc.vars.path
        white_list.reason = vc.vars.reason
        white_list.status = vc.vars.status
        white_list.updated_at = datetime.datetime.now()

        try:
            db.session.add(white_list)
            db.session.commit()
            return jsonify(code=1001, message='update success.')
        except:
            return jsonify(code=4001, message='unknown error.')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        white_list = CobraWhiteList.query.filter_by(id=wid).first()
        data = {
            'title': 'Edit white-list',
            'type': 'edit',
            'rules': rules,
            'projects': projects,
            'whitelist': white_list,
            'id': wid
        }
        return render_template('backend/white-list/edit.html', data=data)
