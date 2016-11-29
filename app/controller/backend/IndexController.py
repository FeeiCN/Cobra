# -*- coding: utf-8 -*-

"""
    backend.index
    ~~~~~~~~~~~~~

    Implements index controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time
import operator
from flask import redirect, request, session, escape, render_template
from sqlalchemy.sql import func, and_
from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraAdminUser, CobraResults, CobraProjects, CobraTaskInfo, CobraRules, CobraVuls
from utils.common import convert_number

__author__ = "lightless"
__email__ = "root@lightless.me"


# login page and index
@web.route(ADMIN_URL + '/', methods=['GET'])
@web.route(ADMIN_URL + '/index', methods=['GET', 'POST'])
def index():
    if ValidateClass.check_login():
        return redirect(ADMIN_URL + '/overview')

    if request.method == "POST":

        vc = ValidateClass(request, 'username', 'password')
        ret, msg = vc.check_args()

        if not ret:
            return msg

        au = CobraAdminUser.query.filter_by(username=vc.vars.username).first()
        if not au or not au.verify_password(vc.vars.password):
            # login failed.
            return "Wrong username or password."
        else:
            # login success.
            session['role'] = au.role
            session['username'] = escape(au.username)
            session['is_login'] = True

            current_time = time.strftime('%Y-%m-%d %X', time.localtime())
            au.last_login_time = current_time
            au.last_login_ip = request.remote_addr
            db.session.add(au)
            db.session.commit()

            return "Login success, jumping...<br /><script>window.setTimeout(\"location='overview'\", 1000);</script>"
    else:
        return render_template("backend/index/index.html")


# main view
@web.route(ADMIN_URL + '/overview', methods=['GET'])
@login_required
def main():
    # amount
    fixed_amount = CobraResults.query.filter(CobraResults.status == 2).count()
    not_fixed_amount = CobraResults.query.filter(CobraResults.status < 2).count()
    projects_amount = CobraProjects.query.count()
    tasks_amount = CobraTaskInfo.query.count()
    files_amount = db.session.query(func.sum(CobraTaskInfo.file_count).label('files')).first()[0]
    lines_amount = db.session.query(func.sum(CobraTaskInfo.code_number).label('codes')).first()[0]
    rules_on = CobraRules.query.filter(CobraRules.status == 1).count()
    rules_off = CobraRules.query.filter(CobraRules.status == 0).count()

    # ranks & hits
    hit_rules = db.session.query(
        func.count(CobraResults.rule_id).label("cnt"), CobraRules.author, CobraRules.description, CobraRules.id
    ).outerjoin(
        CobraRules, CobraResults.rule_id == CobraRules.id
    ).group_by(CobraResults.rule_id).all()
    ranks = dict()
    hits = dict()
    hits_tmp = []
    for res in hit_rules:
        if len(ranks) < 7:
            # ranks
            if res[1] in ranks:
                rank = ranks[res[1]] + res[0]
            else:
                rank = res[0]
            ranks[res[1]] = rank
            # hits
            if res[3] in hits:
                rank = ranks[res[3]] + res[0]
            else:
                rank = res[0]
            hits[res[3]] = {
                'name': res[2],
                'author': res[1],
                'rank': rank
            }
    for h in hits.values():
        hits_tmp.append(h)
    ranks = sorted(ranks.items(), key=operator.itemgetter(1), reverse=True)
    hits = sorted(hits_tmp, key=lambda x: x['rank'], reverse=True)

    rule_amount = db.session.query(CobraRules.author, func.count("*").label('counts')).group_by(CobraRules.author).all()
    rule_amount = sorted(rule_amount, key=operator.itemgetter(1), reverse=True)
    rule_amount_rank = []
    for ra in rule_amount:
        count = CobraRules.query.with_entities(CobraRules.id).filter(CobraRules.author == ra[0], CobraRules.status == 0).count()
        rule_amount_rank.append({
            'author': ra[0],
            'active': ra[1] - count,
            'not_active': count,
            'total': ra[1]
        })

    # vulnerabilities types
    cobra_rules = db.session.query(CobraRules.id, CobraRules.vul_id).all()
    cobra_vuls = db.session.query(CobraVuls.id, CobraVuls.name).all()

    all_rules = {}
    for x in cobra_rules:
        all_rules[x.id] = x.vul_id  # rule_id -> vul_id
    all_cobra_vuls = {}
    for x in cobra_vuls:
        all_cobra_vuls[x.id] = x.name  # vul_id -> vul_name
    # show all vulns
    all_vulnerabilities = db.session.query(
        CobraResults.rule_id, func.count("*").label('counts')
    ).group_by(CobraResults.rule_id).all()

    vulnerabilities_types = []
    for x in all_vulnerabilities:  # all_vuls: results group by rule_id and count(*)
        t = {}
        # get vul name
        if x.rule_id not in all_rules:
            continue
        te = all_cobra_vuls[all_rules[x.rule_id]]
        # check if there is already a same vul name in different language
        flag = False
        for tv in vulnerabilities_types:
            if te == tv['name']:
                tv['amount'] += x.counts
                flag = True
                break
        if not flag:
            t['name'] = all_cobra_vuls[all_rules[x.rule_id]]
            t['amount'] = x.counts
        if t:
            vulnerabilities_types.append(t)
    vulnerabilities_types = sorted(vulnerabilities_types, key=lambda x: x['amount'], reverse=True)

    data = {
        'amount': {
            'vulnerabilities_fixed': convert_number(fixed_amount),
            'vulnerabilities_not_fixed': convert_number(not_fixed_amount),
            'vulnerabilities_total': convert_number(fixed_amount + not_fixed_amount),
            'projects': convert_number(projects_amount),
            'tasks': convert_number(tasks_amount),
            'files': convert_number(files_amount),
            'lines': convert_number(lines_amount),
            'rules_on': convert_number(rules_on),
            'rules_off': convert_number(rules_off),
            'rules_total': convert_number(rules_on + rules_off),
            'rule': rule_amount_rank
        },
        'ranks': ranks,
        'hits': hits,
        'vulnerabilities_types': vulnerabilities_types
    }
    return render_template("backend/index/overview.html", data=data)
