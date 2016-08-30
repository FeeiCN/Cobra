# -*- coding: utf-8 -*-

"""
    backend.vuln
    ~~~~~~~~~~~~

    Implements vuln controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time

from flask import request, jsonify, render_template

from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraVuls

__author__ = "lightless"
__email__ = "root@lightless.me"


# add new vuls button
@web.route(ADMIN_URL + '/add_new_vul', methods=['GET', 'POST'])
@login_required
def add_new_vul():

    if request.method == 'POST':

        vc = ValidateClass(request, "name", "description", "repair")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        vul = CobraVuls(vc.vars.name, vc.vars.description, vc.vars.repair, current_time, current_time)
        try:
            db.session.add(vul)
            db.session.commit()
            return jsonify(tag='success', msg='Add Success.')
        except:
            return jsonify(tag='danger', msg='Add failed. Please try again later.')
    else:
        return render_template('backend/vul/add_new_vul.html')


# show all vuls click
@web.route(ADMIN_URL + '/vuls/<int:page>', methods=['GET'])
@login_required
def vuls(page):

    per_page_vuls = 10
    all_vuls = CobraVuls.query.order_by(CobraVuls.id.desc()).limit(per_page_vuls).offset((page-1)*per_page_vuls).all()
    data = {
        'vuls': all_vuls
    }
    return render_template('backend/vul/vuls.html', data=data)


# del special vul
@web.route(ADMIN_URL + '/del_vul', methods=['POST'])
@login_required
def del_vul():

    vc = ValidateClass(request, "vul_id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    if vc.vars.vul_id:
        v = CobraVuls.query.filter_by(id=vc.vars.vul_id).first()
        try:
            db.session.delete(v)
            db.session.commit()
            return jsonify(tag='success', msg='delete success.')
        except:
            return jsonify(tag='danger', msg='delete failed. Try again later?')
    else:
        return jsonify(tag='danger', msg='wrong id')


# edit special vul
@web.route(ADMIN_URL + '/edit_vul/<int:vul_id>', methods=['GET', 'POST'])
@login_required
def edit_vul(vul_id):

    if request.method == 'POST':

        vc = ValidateClass(request, "name", "description", "repair")
        ret, msg = vc.check_args()

        if not ret:
            return jsonify(tag="danger", msg=msg)

        v = CobraVuls.query.filter_by(id=vul_id).first()
        v.name = vc.args.name
        v.description = vc.args.description
        v.repair = vc.args.repair

        try:
            db.session.add(v)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        v = CobraVuls.query.filter_by(id=vul_id).first()
        return render_template('backend/vul/edit_vul.html', data={
            'vul': v,
        })

