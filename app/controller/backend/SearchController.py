# -*- coding: utf-8 -*-

"""
    backend.search
    ~~~~~~~~~~~~~~

    Implements search controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
from flask import request, render_template, jsonify

from . import ADMIN_URL
from app import web
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraLanguages, CobraVuls, CobraRules

__author__ = "lightless"
__email__ = "root@lightless.me"


# search_rules_bar
@web.route(ADMIN_URL + '/search_rules_bar', methods=['GET'])
@login_required
def search_rules_bar():
    languages = CobraLanguages.query.all()
    vuls = CobraVuls.query.all()

    data = {
        'languages': languages,
        'vuls': vuls,
    }

    return render_template('backend/index/search_rules_bar.html', data=data)


# search rules
@web.route(ADMIN_URL + '/search_rules', methods=['POST'])
@login_required
def search_rules():
    if request.method == 'POST':

        vc = ValidateClass(request, "language", "vul")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        if vc.vars.language == 'all' and vc.vars.vul == 'all':
            rules = CobraRules.query.all()
        elif vc.vars.language == 'all' and vc.vars.vul != 'all':
            rules = CobraRules.query.filter_by(vul_id=vc.vars.vul).all()
        elif vc.vars.language != 'all' and vc.vars.vul == 'all':
            rules = CobraRules.query.filter_by(language=vc.vars.language).all()
        elif vc.vars.language != 'all' and vc.vars.vul != 'all':
            rules = CobraRules.query.filter_by(language=vc.vars.language, vul_id=vc.vars.vul).all()
        else:
            return 'error!'

        cobra_vuls = CobraVuls.query.all()
        cobra_lang = CobraLanguages.query.all()
        all_vuls = {}
        all_language = {}
        for vul in cobra_vuls:
            all_vuls[vul.id] = vul.name
        for lang in cobra_lang:
            all_language[lang.id] = lang.language

        # replace id with real name
        for rule in rules:
            try:
                rule.vul_id = all_vuls[rule.vul_id]
            except KeyError:
                rule.vul_id = 'Unknown Type'
            try:
                rule.language = all_language[rule.language]
            except KeyError:
                rule.language = 'Unknown Language'

        data = {
            'rules': rules,
        }

        return render_template('backend/rule/rules.html', data=data)
