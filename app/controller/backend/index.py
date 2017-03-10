# -*- coding: utf-8 -*-

"""
    backend.index
    ~~~~~~~~~~~~~

    Implements index controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
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
from app import web, db, cache
from utils.validate import ValidateClass, login_required
from app.models import CobraAdminUser, CobraResults, CobraProjects, CobraTaskInfo, CobraRules, CobraVuls
from utils.common import convert_number


# Take all parameters as a cache key
def cache_key():
    return request.url


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
@cache.cached(timeout=3600, key_prefix=cache_key)
def main():
    # is capture
    # True:  nav will hidden
    # False: nope
    capture = request.args.get('capture')
    month = request.args.get('month')
    # time type
    date = datetime.datetime.now()
    c_month = int(date.strftime('%m'))
    c_day = int(date.strftime('%d'))
    c_year = int(date.strftime('%Y'))
    c_quarter = 0
    day_first = ''
    day_last = ''
    c_quarter_first = 0
    c_quarter_last = 0
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
    if time_type not in ['w', 'm', 'q', 'a']:
        # default tt
        time_type = 'w'

    # calculate first day/last day and VT's x axis data
    c_mark = '#'
    trend_scan = {
        'file': [],
        'line': [],
        'project': [],
        'task': []
    }
    amount_vulnerability = {
        'new': {
            'total': 0,
            'time_type': 0
        },
        'fixed': {
            'total': 0,
            'time_type': 0
        }
    }
    # Vulnerability Trend (VT)
    vt_x = []
    if time_type == 'm':
        p_month = 0
        if month is None:
            p_month = int(time.strftime('%m', time.localtime()))
        elif int(month) <= 12:
            p_month = int(month)

        current_time = time.strftime('%Y-{month}-{day}', time.localtime())
        day_first = current_time.format(month=p_month, day=1)
        day_last = current_time.format(month=p_month, day=31)

        for month in range(1, 13):
            x_time = '{month}月'.format(month=month)
            c_year = int(time.strftime('%Y', time.localtime()))
            start = '{year}-{month}-{day}'.format(year=c_year, month=month, day=1)
            next_month = datetime.date(c_year, month, 1).replace(day=28) + datetime.timedelta(days=4)
            end = next_month - datetime.timedelta(days=next_month.day)
            x_data = CobraResults.count_by_time(start, end)
            x_data['t'] = x_data[0] + x_data[1] + x_data[2]
            if month == p_month:
                amount_vulnerability['new']['time_type'] += x_data['t']
                amount_vulnerability['fixed']['time_type'] += x_data[2]
            vt_x.append({
                'time': x_time,
                'data': x_data
            })

    elif time_type == 'q':
        for q in range(1, 5):
            x_time = 'Q{quarter}'.format(quarter=q)
            s_month = 0
            e_month = 0
            if q == 1:
                s_month = 1
                e_month = 3
            elif q == 2:
                s_month = 4
                e_month = 6
            elif q == 3:
                s_month = 7
                e_month = 9
            elif q == 4:
                s_month = 10
                e_month = 12
            cm, last_day = calendar.monthrange(c_year, e_month)
            start = '{year}-{month}-{day}'.format(year=c_year, month=s_month, day=1)
            end = '{year}-{month}-{day}'.format(year=c_year, month=e_month, day=last_day)
            x_data = CobraResults.count_by_time(start, end)
            x_data['t'] = x_data[0] + x_data[1] + x_data[2]
            if q == c_quarter:
                amount_vulnerability['new']['time_type'] += x_data['t']
                amount_vulnerability['fixed']['time_type'] += x_data[2]
            vt_x.append({
                'time': x_time,
                'data': x_data
            })
        cm, last_day = calendar.monthrange(c_year, c_quarter_last)
        day_first = '{0}-{1}-{2}'.format(c_year, c_quarter_first, 1)
        day_last = '{0}-{1}-{2}'.format(c_year, c_quarter_last, last_day)
    else:
        # default TT(time type): w(weekly)
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
            if d == 0:
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
            localtime = time.localtime(time.time() + (d * 86400))
            start_end = time.strftime('%Y-%m-%d', localtime)
            x_data = CobraResults.count_by_time(start_end, start_end)
            x_data['t'] = x_data[0] + x_data[1] + x_data[2]
            amount_vulnerability['new']['time_type'] += x_data['t']
            amount_vulnerability['fixed']['time_type'] += x_data[2]
            vt_x.append({
                'time': x_time,
                'data': x_data
            })
            # scan trend data
            for k in trend_scan:
                start = time.strftime('%Y-%m-%d', time.localtime(time.time() + (d * 86400)))
                ct_count = CobraTaskInfo.count_by_time(start, start, k)
                if ct_count is None:
                    ct_count = 0
                trend_scan[k].append(ct_count)
        if time_type == 'a':
            day_first = '1997-10-10'
            day_last = time.strftime('%Y-%m-%d', time.localtime())

    # Vulnerability Data (VD)
    fixed_amount = db.session.query(
        func.count(CobraResults.id).label('count')
    ).filter(
        CobraResults.status == 2,
        # Active project
        CobraProjects.status > 0,
        CobraResults.project_id == CobraProjects.id
    ).group_by(CobraResults.status).first()
    fixed_amount = fixed_amount[0] if fixed_amount else 0

    not_fixed_amount = db.session.query(
        func.count(CobraResults.id).label('count')
    ).filter(
        CobraResults.status < 2,
        # Active project
        CobraProjects.status > 0,
        CobraResults.project_id == CobraProjects.id
    ).group_by(CobraResults.status).first()
    not_fixed_amount = not_fixed_amount[0] if not_fixed_amount else 0

    # Scan Data (SD)
    project_total = CobraProjects.query.filter(CobraProjects.status > 0).count()

    task_total = db.session.query(
        func.count(CobraTaskInfo.id).label('count')
    ).filter(
        CobraProjects.status > 0,
        CobraProjects.repository == CobraTaskInfo.target
    ).first()[0]

    file_total = db.session.query(
        func.sum(CobraTaskInfo.file_count).label('files')
    ).filter(
        CobraProjects.status > 0,
        CobraProjects.repository == CobraTaskInfo.target
    ).first()[0]

    line_total = db.session.query(
        func.sum(CobraTaskInfo.code_number).label('codes')
    ).filter(
        CobraProjects.status > 0,
        CobraProjects.repository == CobraTaskInfo.target
    ).first()[0]

    amount_scan = {
        'projects': {
            'total': convert_number(project_total),
            'time_type': convert_number(CobraTaskInfo.count_by_time(day_first, day_last, 'project'))
        },
        'tasks': {
            'total': convert_number(task_total),
            'time_type': convert_number(CobraTaskInfo.count_by_time(day_first, day_last, 'task'))
        },
        'files': {
            'total': convert_number(file_total),
            'time_type': convert_number(CobraTaskInfo.count_by_time(day_first, day_last, 'file'))
        },
        'lines': {
            'total': convert_number(line_total),
            'time_type': convert_number(CobraTaskInfo.count_by_time(day_first, day_last, 'line'))
        }
    }

    # Rule Data (RD)
    rule_amount_status = CobraRules.count_by_time(day_first, day_last)
    amount_rule = {
        'on': {
            'total': CobraRules.query.filter(CobraRules.status == 1).count(),
            'time_type': rule_amount_status[1]
        },
        'off': {
            'total': CobraRules.query.filter(CobraRules.status == 0).count(),
            'time_type': rule_amount_status[0]
        },
        'total': {
            'total': 0,
            'time_type': 0
        }
    }
    amount_rule['total']['total'] = convert_number(amount_rule['on']['total'] + amount_rule['off']['total'])
    amount_rule['total']['time_type'] = convert_number(amount_rule['on']['time_type'] + amount_rule['off']['time_type'])
    amount_rule['on']['total'] = convert_number(amount_rule['on']['total'])
    amount_rule['on']['time_type'] = convert_number(amount_rule['on']['time_type'])
    amount_rule['off']['total'] = convert_number(amount_rule['off']['total'])
    amount_rule['off']['time_type'] = convert_number(amount_rule['off']['time_type'])

    # Rule Hits Rank (RHR)
    hit_rules = db.session.query(
        func.count(CobraResults.rule_id).label("cnt"),
        CobraRules.author,
        CobraRules.description,
        CobraRules.id,
    ).filter(
        CobraResults.created_at >= '{start} 00:00:00'.format(start=day_first),
        CobraResults.created_at <= '{end} 23:59:59'.format(end=day_last),
        CobraProjects.status > 0,
        CobraResults.project_id == CobraProjects.id,
        CobraResults.rule_id == CobraRules.id
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

    # new & improves rule (NIR)
    filter_group = (CobraRules.id > 0,)
    filter_group += (CobraRules.updated_at >= '{start} 00:00:00'.format(start=day_first), CobraRules.updated_at <= '{end} 23:59:59'.format(end=day_last),)
    new_rules = db.session.query(CobraRules.author, CobraRules.description).filter(*filter_group).all()
    if len(new_rules) == 0:
        new_rules = [{
            'author': 'Unknown',
            'description': 'Nothing'
        }]

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
    cobra_vulnerabilities = db.session.query(CobraVuls.id, CobraVuls.name).all()

    all_rules = {}
    for x in cobra_rules:
        all_rules[x.id] = x.vul_id  # rule_id -> vul_id
    all_cobra_vulnerabilities = {}
    for x in cobra_vulnerabilities:
        all_cobra_vulnerabilities[x.id] = x.name  # vul_id -> vul_name
    # VTD
    # show all vulnerabilities
    all_vulnerabilities = db.session.query(
        CobraResults.rule_id, func.count("*").label('counts')
    ).filter(
        CobraResults.updated_at >= '{start} 00:00:00'.format(start=day_first),
        CobraResults.updated_at <= '{end} 23:59:59'.format(end=day_last),
        # Active project
        CobraProjects.status > 0,
        CobraResults.project_id == CobraProjects.id
    ).group_by(CobraResults.rule_id).all()

    vulnerabilities_types = []
    for x in all_vulnerabilities:  # results group by rule_id and count(*)
        t = {}
        # get vul name
        if x.rule_id not in all_rules:
            continue
        te = all_cobra_vulnerabilities[all_rules[x.rule_id]]
        # check if there is already a same vul name in different language
        flag = False
        for tv in vulnerabilities_types:
            if te == tv['name']:
                tv['amount'] += x.counts
                flag = True
                break
        if not flag:
            t['name'] = all_cobra_vulnerabilities[all_rules[x.rule_id]]
            t['amount'] = x.counts
        if t:
            vulnerabilities_types.append(t)
    vulnerabilities_types = sorted(vulnerabilities_types, key=lambda x: x['amount'], reverse=True)

    time_type_desc = {
        'w': '周',
        'm': '月',
        'q': '季度',
        'a': '全部'
    }
    ttd = time_type_desc[time_type]
    comment_scan = '本{ttd}扫描数据各指标都比较平稳，无明显波动!'.format(ttd=ttd)
    if amount_rule['total']['time_type'] == 0:
        comment_rule = '本{ttd}没有新增规则'.format(ttd=ttd)
    else:
        comment_rule = '本{ttd}新增{count}条规则'.format(ttd=ttd, count=amount_rule['total']['time_type'])

    comment_vulnerability = '本{ttd}扫出{new}个新漏洞, 修复了{fixed}个漏洞，待修复漏洞进入漏洞修复跟进流程。'.format(ttd=ttd, new=amount_vulnerability['new']['time_type'], fixed=amount_vulnerability['fixed']['time_type'])

    data = {
        'amount': {
            'vulnerabilities_fixed': convert_number(fixed_amount),
            'vulnerabilities_not_fixed': convert_number(not_fixed_amount),
            'vulnerabilities_total': convert_number(fixed_amount + not_fixed_amount),
            'scan': amount_scan,
            'rule': amount_rule,
            'rar': rule_amount_rank
        },
        'trend': {
            'scan': trend_scan
        },
        'comment': {
            'scan': comment_scan,
            'rule': comment_rule,
            'vulnerability': comment_vulnerability
        },
        'ranks': ranks,
        'hits': hits,
        'rules': new_rules,
        'vulnerabilities_types': vulnerabilities_types,
        'time_type': time_type,
        'vt_x': vt_x,
        'day_first': day_first,
        'day_last': day_last,
        'capture': capture
    }
    return render_template("backend/index/overview.html", data=data)
