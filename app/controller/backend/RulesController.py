# -*- coding: utf-8 -*-

"""
    backend.rules
    ~~~~~~~~~~~~~

    Implements rules controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time
import datetime

from flask import redirect, render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import ADMIN_URL
from app import web, db
from app.models import CobraRules, CobraVuls, CobraLanguages
from app.CommonClass.ValidateClass import ValidateClass
from app.CommonClass.ValidateClass import login_required

__author__ = "lightless"
__email__ = "root@lightless.me"


# all rules button
@web.route(ADMIN_URL + '/rules/<int:page>', methods=['GET'])
@login_required
def rules(page):

    per_page = 10
    cobra_rules = CobraRules.query.order_by(CobraRules.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    cobra_vuls = CobraVuls.query.all()
    cobra_lang = CobraLanguages.query.all()
    all_vuls = {}
    all_language = {}
    all_level = {1: 'Low', 2: 'Medium', 3: 'High'}
    for vul in cobra_vuls:
        all_vuls[vul.id] = vul.name
    for lang in cobra_lang:
        all_language[lang.id] = lang.language

    # replace id with real name
    status_desc = {1: 'ON', 0: 'OFF'}
    for rule in cobra_rules:
        try:
            rule.vul_id = all_vuls[rule.vul_id]
        except KeyError:
            rule.vul_id = 'Unknown Type'

        try:
            rule.status = status_desc[rule.status]
        except KeyError:
            rule.status = 'Unknown'

        try:
            rule.language = all_language[rule.language]
        except KeyError:
            rule.language = 'Unknown Language'

        try:
            rule.level = all_level[rule.level]
        except KeyError:
            rule.level = 'Unknown Level'

    data = {
        # 'paginate': cobra_rules,
        'rules': cobra_rules,
    }

    return render_template('backend/rule/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/add_new_rule', methods=['GET', 'POST'])
@login_required
def add_new_rule():

    if request.method == 'POST':
        vc = ValidateClass(request, 'vul_type', 'language', 'regex_location', 'regex_repair', 'repair_block',
                           'description', 'repair', 'level')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = datetime.datetime.now()
        rule = CobraRules(
            vul_id=vc.vars.vul_type,
            language=vc.vars.language,
            regex_location=vc.vars.regex_location,
            regex_repair=vc.vars.regex_repair,
            block_repair=vc.vars.repair_block,
            description=vc.vars.description,
            repair=vc.vars.repair,
            status=1,
            level=vc.vars.level,
            created_at=current_time,
            updated_at=current_time
        )
        try:
            db.session.add(rule)
            db.session.commit()
            return jsonify(tag='success', msg='add success.')
        except Exception as e:
            return jsonify(tag='danger', msg='add failed, try again later?' + e.message)
    else:
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        data = {
            'vul_type': vul_type,
            'languages': languages
        }
        return render_template('backend/rule/add_new_rule.html', data=data)


# del special rule
@web.route(ADMIN_URL + '/del_rule', methods=['POST'])
@login_required
def del_rule():

    vc = ValidateClass(request, "rule_id")
    vc.check_args()
    vul_id = vc.vars.rule_id
    if vul_id:
        r = CobraRules.query.filter_by(id=vul_id).first()
        try:
            db.session.delete(r)
            db.session.commit()
            return jsonify(tag='success', msg='delete success.')
        except:
            return jsonify(tag='danger', msg='delete failed. Try again later?')
    else:
        return jsonify(tag='danger', msg='wrong id')


# edit special rule
@web.route(ADMIN_URL + '/edit_rule/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):

    if request.method == 'POST':

        vc = ValidateClass(request, "vul_type", "language", "regex_location", "regex_repair", "block_repair",
                           "description", "rule_id", "repair", "status", "level")
        ret, msg = vc.check_args()

        if not ret:
            return jsonify(tag="danger", msg=msg)

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vc.vars.vul_type
        r.language = vc.vars.language
        r.block_repair = vc.vars.block_repair
        r.regex_location = vc.vars.regex_location
        r.regex_repair = vc.vars.regex_repair
        r.description = vc.vars.description
        r.repair = vc.vars.repair
        r.status = vc.vars.status
        r.level = vc.vars.level
        r.updated_at = datetime.datetime.now()
        try:
            db.session.add(r)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except SQLAlchemyError:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        r = CobraRules.query.filter_by(id=rule_id).first()
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        return render_template('backend/rule/edit_rule.html', data={
            'rule': r,
            'all_vuls': vul_type,
            'all_lang': languages,
        })
