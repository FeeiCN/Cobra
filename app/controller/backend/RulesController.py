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
import datetime

from flask import render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import ADMIN_URL
from app import web, db
from app.models import CobraRules, CobraVuls, CobraLanguages, CobraResults
from app.CommonClass.ValidateClass import ValidateClass
from app.CommonClass.ValidateClass import login_required

__author__ = "lightless"
__email__ = "root@lightless.me"


# all rules button
@web.route(ADMIN_URL + '/rules/', methods=['GET'], defaults={'page': 1})
@web.route(ADMIN_URL + '/rules/<int:page>', methods=['GET'])
@login_required
def rules(page):
    per_page = 10
    rules = CobraRules.query.order_by(CobraRules.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    data = {
        'rules': rules,
        'page': page
    }
    return render_template('backend/rule/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/rules/add/', methods=['GET', 'POST'])
@login_required
def add_new_rule():
    if request.method == 'POST':
        vc = ValidateClass(request, 'vul_type', 'language', 'regex_location', 'repair_block',
                           'description', 'repair', 'author', 'level', 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4004, message=msg)

        current_time = datetime.datetime.now()
        rule = CobraRules(
            vul_id=vc.vars.vul_type,
            language=vc.vars.language,
            regex_location=vc.vars.regex_location,
            regex_repair=request.form.get("regex_repair", ""),
            block_repair=vc.vars.repair_block,
            description=vc.vars.description,
            repair=vc.vars.repair,
            author=vc.vars.author,
            status=vc.vars.status,
            level=vc.vars.level,
            created_at=current_time,
            updated_at=current_time
        )
        try:
            db.session.add(rule)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except Exception as e:
            return jsonify(code=1004, message='add failed, try again later?' + e.message)
    else:
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        data = {
            'type': 'add',
            'title': 'Create rule',
            'all_vuls': vul_type,
            'all_lang': languages,
            'rule': dict()
        }
        return render_template('backend/rule/edit.html', data=data)


# del special rule
@web.route(ADMIN_URL + '/rules/del/', methods=['POST'])
@login_required
def del_rule():
    vc = ValidateClass(request, "id")
    vc.check_args()
    rule_id = vc.vars.id
    if rule_id:

        # 检查该条rule是否存在result和task的依赖
        result = db.session.query(
            CobraResults.task_id
        ).filter(CobraResults.rule_id == rule_id).group_by(CobraResults.task_id).all()
        if len(result):
            # 存在依赖
            task_rely = ""
            for res in result:
                task_rely += str(res.task_id) + ","
            task_rely = task_rely.strip(",")
            message = "Delete failed. Please check and delete the task rely on this rule first.<br />"
            message += "<strong>Rely Tasks: </strong>" + task_rely

            return jsonify(code=1004, message=message)

        r = CobraRules.query.filter_by(id=rule_id).first()
        try:
            db.session.delete(r)
            db.session.commit()
            return jsonify(code=1001, message='delete success.')
        except SQLAlchemyError:
            return jsonify(code=1004, message='delete failed. Try again later?')
    else:
        return jsonify(code=1004, message='wrong id')


# edit special rule
@web.route(ADMIN_URL + '/rules/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    if request.method == 'POST':

        vc = ValidateClass(request, "vul_type", "language", "regex_location", "repair_block", "description",
                           "rule_id", "repair", "author", "status", "level")
        ret, msg = vc.check_args()

        regex_repair = request.form.get("regex_repair", "")

        if not ret:
            return jsonify(code=4004, message=msg)

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vc.vars.vul_type
        r.language = vc.vars.language
        r.block_repair = vc.vars.repair_block
        r.regex_location = vc.vars.regex_location
        r.regex_repair = regex_repair
        r.description = vc.vars.description
        r.repair = vc.vars.repair
        r.author = vc.vars.author
        r.status = vc.vars.status
        r.level = vc.vars.level
        r.updated_at = datetime.datetime.now()
        try:
            db.session.add(r)
            db.session.commit()
            return jsonify(code=1001, message='success')
        except SQLAlchemyError:
            return jsonify(code=4004, message='save failed. Try again later?')
    else:
        r = CobraRules.query.filter_by(id=rule_id).first()
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        return render_template('backend/rule/edit.html', data={
            'type': 'edit',
            'title': 'Edit rule',
            'id': r.id,
            'rule': r,
            'all_vuls': vul_type,
            'all_lang': languages,
        })


@web.route(ADMIN_URL + "/rules/search/<keyword>", methods=['GET'])
@login_required
def search_rule(keyword):
    rules = CobraRules.query.filter(CobraRules.description.like("%{}%".format(keyword))).all()
    data = {
        'rules': rules,
        'keyword': keyword
    }
    return render_template('backend/rule/rules.html', data=data)
