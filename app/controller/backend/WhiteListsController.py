# -*- coding: utf-8 -*-

"""
    backend.whitelist
    ~~~~~~~~~~~~~~~~~

    Implements whitelist controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time

from flask import jsonify, render_template, request

from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraWhiteList, CobraRules, CobraProjects

__author__ = "lightless"
__email__ = "root@lightless.me"


# show all white lists
@web.route(ADMIN_URL + '/whitelists/<int:page>', methods=['GET'])
@login_required
def whitelists(page):

    per_page = 10
    whitelists = CobraWhiteList.query.order_by(CobraWhiteList.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    data = {
        'whitelists': whitelists,
    }
    return render_template('backend/whitelist/whitelists.html', data=data)


# add new white list
@web.route(ADMIN_URL + '/add_whitelist', methods=['GET', 'POST'])
@login_required
def add_whitelist():

    if request.method == 'POST':

        vc = ValidateClass(request, "project_id", "rule_id", "path", "reason")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if vc.vars.path[0] != '/':
            vc.vars.path = '/' + vc.vars.path
        whitelist = CobraWhiteList(vc.vars.project_id, vc.vars.rule_id, vc.vars.path, vc.vars.reason,
                                   1, current_time, current_time)
        try:
            db.session.add(whitelist)
            db.session.commit()
            return jsonify(tag='success', msg='add success.')
        except:
            return jsonify(tag='danger', msg='unknown error. Try again later?')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        data = {
            'rules': rules,
            'projects': projects,
        }
        return render_template('backend/whitelist/add_new_whitelist.html', data=data)


# del the special white list
@web.route(ADMIN_URL + '/del_whitelist', methods=['POST'])
@login_required
def del_whitelist():

    vc = ValidateClass(request, "whitelist_id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    whitelist = CobraWhiteList.query.filter_by(id=vc.vars.whitelist_id).first()
    try:
        db.session.delete(whitelist)
        db.session.commit()
        return jsonify(tag='success', msg='delete success.')
    except:
        return jsonify(tag='danger', msg='unknown error.')


# edit the special white list
@web.route(ADMIN_URL + '/edit_whitelist/<int:whitelist_id>', methods=['GET', 'POST'])
@login_required
def edit_whitelist(whitelist_id):

    if request.method == 'POST':

        vc = ValidateClass(request, "whitelist_id", "project", "rule", "path", "reason", "status")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
        if not whitelist:
            return jsonify(tag='danger', msg='wrong whitelist')

        whitelist.project_id = vc.vars.project_id
        whitelist.rule_id = vc.vars.rule_id
        whitelist.path = vc.vars.path
        whitelist.reason = vc.vars.reason
        whitelist.status = vc.vars.status

        try:
            db.session.add(whitelist)
            db.session.commit()
            return jsonify(tag='success', msg='update success.')
        except:
            return jsonify(tag='danger', msg='unknown error.')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
        data = {
            'rules': rules,
            'projects': projects,
            'whitelist': whitelist,
        }

        return render_template('backend/whitelist/edit_whitelist.html', data=data)

