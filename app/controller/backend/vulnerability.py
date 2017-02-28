# -*- coding: utf-8 -*-

"""
    backend.vulnerability
    ~~~~~~~~~~~~~~~~~~~~~

    Implements vulnerability controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
from flask import request, jsonify, render_template
from . import ADMIN_URL
from app import web, db
from utils.validate import ValidateClass, login_required
from app.models import CobraVuls


@web.route(ADMIN_URL + '/vulnerability/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/vulnerability/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/vulnerability/<int:page>/<keyword>', methods=['GET'])
@login_required
def vulnerability_list(page, keyword):
    if keyword != '0':
        filter_group = (CobraVuls.name.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraVuls.id > 0)
    per_page = 10
    vulnerability = CobraVuls.query.filter(filter_group).order_by(CobraVuls.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraVuls.query.filter(filter_group).count()

    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'vulnerability': vulnerability,
        'keyword': keyword,
        'page': page
    }
    return render_template('backend/vulnerability/vulnerability.html', data=data)


@web.route(ADMIN_URL + '/vulnerability/create/', methods=['GET', 'POST'])
@login_required
def vulnerability_create():
    if request.method == 'POST':
        vc = ValidateClass(request, "name", "description", "repair", "third_v_id")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        vul = CobraVuls(vc.vars.name, vc.vars.description, vc.vars.repair, vc.vars.third_v_id, current_time, current_time)
        try:
            db.session.add(vul)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except:
            return jsonify(code=4001, message='unknown error. Try again later?')
    else:
        data = {
            'title': 'Create vulnerability',
            'type': 'create',
            'vulnerability': dict()
        }
        return render_template('backend/vulnerability/edit.html', data=data)


# del special vulnerability
@web.route(ADMIN_URL + '/vulnerability/delete', methods=['POST'])
@login_required
def vulnerability_delete():
    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4001, message=msg)
    v = CobraVuls.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(v)
        db.session.commit()
        return jsonify(code=1001, message='delete success.')
    except:
        return jsonify(code=4002, message='unknown error.')


# edit special vulnerability
@web.route(ADMIN_URL + '/vulnerability/edit/<int:vid>', methods=['GET', 'POST'])
@login_required
def vulnerability_edit(vid):
    if request.method == 'POST':
        vc = ValidateClass(request, "name", "description", "repair", "third_v_id")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4001, message=msg)

        v = CobraVuls.query.filter_by(id=vid).first()
        if not v:
            return jsonify(code=4001, message='wrong white-list')

        v.name = vc.vars.name
        v.description = vc.vars.description
        v.repair = vc.vars.repair
        v.third_v_id = vc.vars.third_v_id

        try:
            db.session.add(v)
            db.session.commit()
            return jsonify(code=1001, message='update success.')
        except:
            return jsonify(code=4001, message='unknown error.')
    else:
        vulnerability = CobraVuls.query.filter_by(id=vid).first()
        data = {
            'title': 'Edit vulnerability',
            'type': 'edit',
            'vulnerability': vulnerability,
            'id': vid
        }
        return render_template('backend/vulnerability/edit.html', data=data)
