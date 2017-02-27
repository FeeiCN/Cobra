# -*- coding: utf-8 -*-

"""
    backend.language
    ~~~~~~~~~~~~~~~~

    Implements language controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from flask import request, jsonify, render_template, redirect

from . import ADMIN_URL
from app import web, db
from utils.validate import ValidateClass, login_required
from app.models import CobraLanguages


@web.route(ADMIN_URL + '/language/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/language/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/language/<int:page>/<keyword>', methods=['GET'])
@login_required
def language_list(page, keyword):
    if keyword != '0':
        filter_group = (CobraLanguages.language.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraLanguages.id > 0)
    per_page = 10
    language = CobraLanguages.query.filter(filter_group).order_by(CobraLanguages.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraLanguages.query.filter(filter_group).count()

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'language': language,
        'keyword': keyword,
        'page': page
    }
    return render_template('backend/language/language.html', data=data)


@web.route(ADMIN_URL + '/language/create/', methods=['GET', 'POST'])
@login_required
def language_create():
    if request.method == 'POST':
        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)
        exist = CobraLanguages.query.filter(CobraLanguages.language == vc.vars.language).first()
        if exist is not None:
            return jsonify(code=4001, message='The language exist')
        l = CobraLanguages(vc.vars.language, vc.vars.extensions)
        try:
            db.session.add(l)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except:
            return jsonify(code=4001, message='unknown error. Try again later?')
    else:
        data = {
            'title': 'Create language',
            'type': 'create',
            'language': dict()
        }
        return render_template('backend/language/edit.html', data=data)


@web.route(ADMIN_URL + '/language/delete', methods=['POST'])
@login_required
def language_delete():
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)
    v = CobraLanguages.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except:
        return jsonify(code=4002, message='unknown error.')


@web.route(ADMIN_URL + '/language/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def language_edit(id):
    if request.method == 'POST':
        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        item = CobraLanguages.query.filter_by(id=id).first()
        if not item:
            return jsonify(code=4001, message='wrong white-list')

        item.language = vc.vars.language
        item.extensions = vc.vars.extensions

        try:
            db.session.add(item)
            db.session.commit()
            return jsonify(code=1001, message='update success.')
        except:
            return jsonify(code=4001, message='unknown error.')
    else:
        language = CobraLanguages.query.filter_by(id=id).first()
        data = {
            'title': 'Edit language',
            'type': 'edit',
            'language': language,
            'id': id
        }
        return render_template('backend/language/edit.html', data=data)
