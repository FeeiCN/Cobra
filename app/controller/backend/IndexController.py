# -*- coding: utf-8 -*-

"""
    backend.index
    ~~~~~~~~~~~~~

    Implements index controller

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
import datetime
import operator
import calendar
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
    # time type
    date = datetime.datetime.now()
    c_month = int(date.strftime('%m'))
    c_day = int(date.strftime('%d'))
    c_year = int(date.strftime('%Y'))
    c_quarter = 0
    day_first = ''
    day_last = ''
    if c_month in [1, 2, 3]:
        c_quarter = 1
        c_quarter_first = 1
        c_quarter_last = 3
    elif c_month in [4, 5, 6]:
        c_quarter = 2
        c_quarter_first = 4
        c_quarter_last = 6
    elif c_month in [7, 8, 9]:
        c_quarter = 3
        c_quarter_first = 7
        c_quarter_last = 9
    elif c_month in [10, 11, 12]:
        c_quarter = 4
        c_quarter_first = 10
        c_quarter_last = 12

    # time type
    time_type = request.args.get('tt')
    if time_type not in ['w', 'm', 'q']:
        # default tt
        time_type = 'w'

    # calculate first day/last day and VT's x axis data
    c_mark = '#'
    if time_type == 'm':
        vt_x = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12]
        for i, x in enumerate(vt_x):
            if x == c_month:
                vt_x[i] = '{0}{1}月'.format(c_mark, x)
            else:
                vt_x[i] = '{0}月'.format(x)
        cm, last_day = calendar.monthrange(c_year, c_month)
        day_first = '{0}-{1}-{2}'.format(c_year, c_month, 1)
        day_last = '{0}-{1}-{2}'.format(c_year, c_month, last_day)

        # VT x/y axis data

    elif time_type == 'q':
        vt_x = ['Q1', 'Q2', 'Q3', 'Q4']
        for i, x in enumerate(vt_x):
            if (i + 1) == c_quarter:
                vt_x[i] = '{0}{1}'.format(c_mark, x)
        cm, last_day = calendar.monthrange(c_year, c_quarter_last)
        day_first = '{0}-{1}-{2}'.format(c_year, c_quarter_first, 1)
        day_last = '{0}-{1}-{2}'.format(c_year, c_quarter_last, last_day)
    else:
        # default TT(time type): w(weekly)
        vt_x = []
        week_desc = {
            0: '日',
            1: '一',
            2: '二',
            3: '三',
            4: '四',
            5: '五',
            6: '六'
        }
        for d in range(-7, 1):
            t = time.localtime(time.time() + (d * 86400))
            if d == -7:
                day_first = time.strftime('%Y-%m-%d', t)
            elif d == 0:
                day_last = time.strftime('%Y-%m-%d', t)
            week = int(time.strftime('%w', t))
            week_d = week_desc[week]
            month = int(time.strftime('%m', t))
            day = int(time.strftime('%d', t))
            if day == c_day:
                x_time = '{0}{1}/{2}({3})'.format(c_mark, month, day, week_d)
            else:
                x_time = '{0}/{1}({2})'.format(month, day, week_d)
            # VT x data
            x_data = CobraResults.count_by_day(d)
            x_data['t'] = x_data[0] + x_data[1] + x_data[2]
            vt_x.append({
                'time': x_time,
                'data': x_data
            })
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
        'vulnerabilities_types': vulnerabilities_types,
        'time_type': time_type,
        'vt_x': vt_x,
        'day_first': day_first,
        'day_last': day_last
    }

    return render_template("backend/index/overview.html", data=data)
