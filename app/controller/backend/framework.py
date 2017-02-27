# -*- coding: utf-8 -*-

"""
    backend.framework
    ~~~~~~~~~~~~~~~~~

    Implements framework controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from flask import render_template
from flask import request
from flask import jsonify
from sqlalchemy.exc import SQLAlchemyError

from app import db, web
from app.models import CobraWebFrame, CobraWebFrameRules
from utils.validate import login_required, ValidateClass
from . import ADMIN_URL


@web.route(ADMIN_URL + '/framework/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/framework/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/framework/<int:page>/<keyword>', methods=['GET'])
@login_required
def framework_list(page, keyword):
    if keyword != '0':
        filter_group = (CobraWebFrame.frame_name.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraWebFrame.id > 0)
    per_page = 10

    framework = CobraWebFrame.query.filter(filter_group).order_by(CobraWebFrame.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    # framework = db.session.query(
    #     CobraWebFrame.frame_name, CobraWebFrame.description, CobraWebFrameRules.path_rule,
    #     CobraWebFrameRules.content_rule, CobraWebFrameRules.status, CobraWebFrameRules.id
    # ).filter(CobraWebFrameRules.frame_id == CobraWebFrame.id).order_by(CobraWebFrame.id.desc()).limit(per_page).offset((page - 1) * per_page).all()

    total = CobraWebFrame.query.filter(filter_group).count()

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'framework': framework,
        'keyword': keyword,
        'page': page
    }
    return render_template('backend/framework/framework.html', data=data)


@web.route(ADMIN_URL + '/framework/rule/<int:fid>', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/framework/rule/<int:fid>/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/framework/rule/<int:fid>/<int:page>/<keyword>', methods=['GET'])
@login_required
def framework_rule_list(fid, page, keyword):
    if keyword != '0':
        filter_group = (CobraWebFrameRules.path_rule.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraWebFrameRules.frame_id == fid)
    per_page = 10

    framework_rule = CobraWebFrameRules.query.filter(filter_group).order_by(CobraWebFrameRules.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    framework = CobraWebFrame.query.filter(filter_group).first()
    total = CobraWebFrameRules.query.filter(filter_group).count()

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'framework': framework,
        'framework_rule': framework_rule,
        'keyword': keyword,
        'page': page,
        'fid': fid
    }
    return render_template('backend/framework/framework_rule.html', data=data)


@web.route(ADMIN_URL + '/framework/create/', methods=['GET', 'POST'])
@login_required
def framework_create():
    if request.method == 'POST':
        vc = ValidateClass(request, "name", "description")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        item = CobraWebFrame(vc.vars.name, vc.vars.description)
        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except:
            return jsonify(code=4001, message='unknown error. Try again later?')
    else:
        data = {
            'title': 'Create framework',
            'type': 'create',
            'framework': dict()
        }
        return render_template('backend/framework/edit.html', data=data)


@web.route(ADMIN_URL + '/framework/rule/<int:fid>/create/', methods=['GET', 'POST'])
@login_required
def create_framework_rule(fid):
    if request.method == 'POST':
        vc = ValidateClass(request, 'status', 'path', 'content')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        item = CobraWebFrameRules(frame_id=fid, path_rule=vc.vars.path, content_rule=vc.vars.content, status=vc.vars.status)
        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except:
            return jsonify(code=4001, message='unknown error. Try again later?')
    else:
        data = {
            'title': 'Create framework rule',
            'type': 'create',
            'framework_rule': dict(),
            'fid': fid
        }
        return render_template('backend/framework/edit_rule.html', data=data)


@web.route(ADMIN_URL + '/framework/delete', methods=['POST'])
@login_required
def framework_delete():
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)
    v = CobraWebFrame.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except:
        return jsonify(code=4002, message='unknown error.')


@web.route(ADMIN_URL + '/framework/rule/<int:fid>/delete', methods=['POST'])
@login_required
def delete_framework_rule(fid):
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)
    v = CobraWebFrameRules.query.filter_by(id=vc.vars.id, frame_id=fid).first()
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except:
        return jsonify(code=4002, message='unknown error.')


@web.route(ADMIN_URL + '/framework/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def framework_edit(id):
    if request.method == 'POST':
        vc = ValidateClass(request, "name", "description")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        item = CobraWebFrame.query.filter_by(id=id).first()
        if not item:
            return jsonify(code=4001, message='wrong white-list')

        item.frame_name = vc.vars.name
        item.description = vc.vars.description

        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(code=1001, message='update success.')
        except:
            return jsonify(code=4001, message='unknown error.')
    else:
        framework = CobraWebFrame.query.filter_by(id=id).first()
        data = {
            'title': 'Edit framework',
            'type': 'edit',
            'framework': framework,
            'id': id
        }
        return render_template('backend/framework/edit.html', data=data)


@web.route(ADMIN_URL + '/framework/rule/<int:fid>/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit_framework_rule(fid, id):
    if request.method == 'POST':
        vc = ValidateClass(request, 'path', 'content', 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        item = CobraWebFrameRules.query.filter_by(id=id, frame_id=fid).first()
        if not item:
            return jsonify(code=4001, message='wrong white-list')

        item.path_rule = vc.vars.path
        item.content_rule = vc.vars.content
        item.status = vc.vars.status

        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(code=1001, message='update success.')
        except:
            return jsonify(code=4001, message='unknown error.')
    else:
        framework_rule = CobraWebFrameRules.query.filter_by(id=id, frame_id=fid).first()
        data = {
            'title': 'Edit framework rule',
            'type': 'edit',
            'framework_rule': framework_rule,
            'id': id,
            'fid': fid
        }
        return render_template('backend/framework/edit_rule.html', data=data)
