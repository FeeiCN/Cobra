# -*- coding: utf-8 -*-

"""
    backend.dashboard
    ~~~~~~~~~~~~~~~~~

    Implements dashboard controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import time
import datetime

from flask import redirect, jsonify, render_template, request
from sqlalchemy.sql import func, and_

from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass
from app.models import CobraRules, CobraVuls, CobraTaskInfo
from app.models import CobraLanguages, CobraResults, CobraProjects

__author__ = "lightless"
__email__ = "root@lightless.me"


@web.route(ADMIN_URL + "/dashboard", methods=['GET'])
def dashboard():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    cobra_rules = db.session.query(CobraRules.id, CobraRules.vul_id, ).all()
    cobra_vuls = db.session.query(CobraVuls.id, CobraVuls.name).all()

    # get today date time and timestamp
    today_time_array = datetime.date.today()
    today_time_stamp = int(time.mktime(today_time_array.timetuple()))
    tomorrow_time_stamp = today_time_stamp + 3600 * 24
    tomorrow_time_array = datetime.datetime.fromtimestamp(int(tomorrow_time_stamp))

    # total overview
    total_task_count = CobraTaskInfo.query.count()
    total_vulns_count = CobraResults.query.count()
    total_projects_count = CobraProjects.query.count()
    total_files_count = db.session.query(func.sum(CobraTaskInfo.file_count).label('files')).first()[0]
    total_code_number = db.session.query(func.sum(CobraTaskInfo.code_number).label('codes')).first()[0]

    # today overview
    today_task_count = CobraTaskInfo.query.filter(
        and_(CobraTaskInfo.time_start >= today_time_stamp, CobraTaskInfo.time_start <= tomorrow_time_stamp)
    ).count()
    today_vulns_count = CobraResults.query.filter(
        and_(CobraResults.created_at >= today_time_array, CobraResults.created_at <= tomorrow_time_array)
    ).count()
    today_projects_count = CobraProjects.query.filter(
        and_(CobraProjects.last_scan >= today_time_array, CobraProjects.last_scan <= tomorrow_time_array)
    ).count()
    today_files_count = db.session.query(func.sum(CobraTaskInfo.file_count).label('files')).filter(
        and_(CobraTaskInfo.time_start >= today_time_stamp, CobraTaskInfo.time_start <= tomorrow_time_stamp)
    ).first()[0]
    today_code_number = db.session.query(func.sum(CobraTaskInfo.code_number).label('codes')).filter(
        and_(CobraTaskInfo.time_start >= today_time_stamp, CobraTaskInfo.time_start <= tomorrow_time_stamp)
    ).first()[0]

    # scanning time
    avg_scan_time = db.session.query(func.avg(CobraTaskInfo.time_consume)).first()[0]
    max_scan_time = db.session.query(func.max(CobraTaskInfo.time_consume)).first()[0]
    min_scan_time = db.session.query(func.min(CobraTaskInfo.time_consume)).first()[0]

    # total each vuls count
    all_vuls = db.session.query(
        CobraResults.rule_id, func.count("*").label('counts')
    ).group_by(CobraResults.rule_id).all()

    # today each vuls count
    all_vuls_today = db.session.query(
        CobraResults.rule_id, func.count("*").label('counts')
    ).group_by(CobraResults.rule_id).filter(
        and_(CobraResults.created_at >= today_time_array, CobraResults.created_at <= tomorrow_time_array)
    ).all()

    all_rules = {}
    for x in cobra_rules:
        all_rules[x.id] = x.vul_id  # rule_id -> vul_id
    all_cobra_vuls = {}
    for x in cobra_vuls:
        all_cobra_vuls[x.id] = x.name  # vul_id -> vul_name

    total_vuls = []
    for x in all_vuls:  # all_vuls: results group by rule_id and count(*)
        t = {}
        # get vul name
        te = all_cobra_vuls[all_rules[x.rule_id]]
        # check if there is already a same vul name in different language
        flag = False
        for tv in total_vuls:
            if te == tv.get('vuls'):
                tv['counts'] += x.counts
                flag = True
                break
        if not flag:
            t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
            t['counts'] = x.counts
        if t:
            total_vuls.append(t)
    today_vuls = []
    for x in all_vuls_today:
        t = {}
        # get vul name
        te = all_cobra_vuls[all_rules[x.rule_id]]
        # check if there is already a same vul name in different language
        flag = False
        for tv in today_vuls:
            if te == tv.get('vuls'):
                tv['counts'] += x.counts
                flag = True
                break
        if not flag:
            t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
            t['counts'] = x.counts
        if t:
            today_vuls.append(t)

    data = {
        'total_task_count': total_task_count,
        'total_vulns_count': total_vulns_count,
        'total_projects_count': total_projects_count,
        'total_files_count': total_files_count,
        'today_task_count': today_task_count,
        'today_vulns_count': today_vulns_count,
        'today_projects_count': today_projects_count,
        'today_files_count': today_files_count,
        'max_scan_time': max_scan_time,
        'min_scan_time': min_scan_time,
        'avg_scan_time': avg_scan_time,
        'total_vuls': total_vuls,
        'today_vuls': today_vuls,
        'total_code_number': total_code_number,
        'today_code_number': today_code_number,
    }
    return render_template("backend/index/dashboard.html", data=data)


@web.route(ADMIN_URL + "/get_scan_information", methods=['POST'])
def get_scan_information():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":
        start_time_stamp = request.form.get("start_time_stamp")[0:10]
        end_time_stamp = request.form.get("end_time_stamp")[0:10]
        start_time_array = datetime.datetime.fromtimestamp(int(start_time_stamp))
        end_time_array = datetime.datetime.fromtimestamp(int(end_time_stamp))

        if start_time_stamp >= end_time_stamp:
            return jsonify(tag="danger", msg="wrong date select.", code=1002)

        task_count = CobraTaskInfo.query.filter(
            and_(CobraTaskInfo.time_start >= start_time_stamp, CobraTaskInfo.time_start <= end_time_stamp)
        ).count()
        vulns_count = CobraResults.query.filter(
            and_(CobraResults.created_at >= start_time_array, CobraResults.created_at <= end_time_array)
        ).count()
        projects_count = CobraProjects.query.filter(
            and_(CobraProjects.last_scan >= start_time_array, CobraProjects.last_scan <= end_time_array)
        ).count()
        files_count = db.session.query(func.sum(CobraTaskInfo.file_count).label('files')).filter(
            and_(CobraTaskInfo.time_start >= start_time_stamp, CobraTaskInfo.time_start <= end_time_stamp)
        ).first()[0]
        code_number = db.session.query(func.sum(CobraTaskInfo.code_number).label('codes')).filter(
            and_(CobraTaskInfo.time_start >= start_time_stamp, CobraTaskInfo.time_start <= end_time_stamp)
        ).first()[0]

        return jsonify(code=1001, task_count=task_count, vulns_count=vulns_count, projects_count=projects_count,
                       files_count=int(files_count), code_number=int(code_number))


@web.route(ADMIN_URL + "/graph_vulns", methods=['POST'])
def graph_vulns():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":
        show_all = request.form.get("show_all")

        cobra_rules = db.session.query(CobraRules.id, CobraRules.vul_id, ).all()
        cobra_vuls = db.session.query(CobraVuls.id, CobraVuls.name).all()

        all_rules = {}
        for x in cobra_rules:
            all_rules[x.id] = x.vul_id  # rule_id -> vul_id
        all_cobra_vuls = {}
        for x in cobra_vuls:
            all_cobra_vuls[x.id] = x.name  # vul_id -> vul_name

        if show_all:
            # show all vulns
            all_vuls = db.session.query(
                CobraResults.rule_id, func.count("*").label('counts')
            ).group_by(CobraResults.rule_id).all()

            total_vuls = []
            for x in all_vuls:  # all_vuls: results group by rule_id and count(*)
                t = {}
                # get vul name
                te = all_cobra_vuls[all_rules[x.rule_id]]
                # check if there is already a same vul name in different language
                flag = False
                for tv in total_vuls:
                    if te == tv['vuls']:
                        tv['counts'] += x.counts
                        flag = True
                        break
                if not flag:
                    t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
                    t['counts'] = x.counts
                if t:
                    total_vuls.append(t)

            return jsonify(data=total_vuls)
        else:
            # show part of vulns
            start_time_stamp = request.form.get("start_time_stamp")[:10]
            end_time_stamp = request.form.get("end_time_stamp")[:10]
            if start_time_stamp >= end_time_stamp:
                return jsonify(code=1002, tag="danger", msg="wrong datetime.")

            start_time = datetime.datetime.fromtimestamp(int(start_time_stamp))
            end_time = datetime.datetime.fromtimestamp(int(end_time_stamp))
            # TODO: improve this
            all_vuls = db.session.query(
                CobraResults.rule_id, func.count("*").label('counts')
            ).filter(
                and_(CobraResults.created_at >= start_time, CobraResults.created_at <= end_time)
            ).group_by(CobraResults.rule_id).all()

            total_vuls = []
            for x in all_vuls:  # all_vuls: results group by rule_id and count(*)
                t = {}
                # get vul name
                te = all_cobra_vuls[all_rules[x.rule_id]]
                # check if there is already a same vul name in different language
                flag = False
                for tv in total_vuls:
                    if te == tv['vuls']:
                        tv['counts'] += x.counts
                        flag = True
                        break
                if not flag:
                    t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
                    t['counts'] = x.counts
                if t:
                    total_vuls.append(t)

            return jsonify(data=total_vuls)


@web.route(ADMIN_URL + "/graph_languages", methods=['POST'])
def graph_languages():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    show_all = request.form.get("show_all")

    return_value = dict()

    if show_all:
        hit_rules = db.session.query(
            func.count(CobraResults.rule_id).label("cnt"), CobraLanguages.language
        ).outerjoin(
            CobraRules, CobraResults.rule_id == CobraRules.id
        ).outerjoin(
            CobraLanguages, CobraRules.language == CobraLanguages.id
        ).group_by(CobraResults.rule_id).all()
    else:
        start_time_stamp = request.form.get("start_time_stamp")
        end_time_stamp = request.form.get("end_time_stamp")
        start_time = datetime.datetime.fromtimestamp(int(start_time_stamp[:10]))
        end_time = datetime.datetime.fromtimestamp(int(end_time_stamp[:10]))
        hit_rules = db.session.query(
            func.count(CobraResults.rule_id).label("cnt"), CobraLanguages.language
        ).outerjoin(
            CobraRules, CobraResults.rule_id == CobraRules.id
        ).outerjoin(
            CobraLanguages, CobraRules.language == CobraLanguages.id
        ).filter(
            and_(CobraResults.created_at >= start_time, CobraResults.created_at <= end_time)
        ).group_by(CobraResults.rule_id).all()

    for res in hit_rules:
        if return_value.get(res[1]):
            return_value[res[1]] += res[0]
        else:
            return_value[res[1]] = res[0]

    return jsonify(data=return_value)


@web.route(ADMIN_URL + "/graph_lines", methods=['POST'])
def graph_lines():
    # everyday vulns count
    # everyday scan count
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')
    show_all = request.form.get("show_all")
    if show_all:
        days = 15 - 1
        vuls = list()
        scans = list()
        labels = list()
        # get vulns count
        end_date = datetime.datetime.today()
        start_date = datetime.date.today() - datetime.timedelta(days=days)
        start_date = datetime.datetime.combine(start_date, datetime.datetime.min.time())

        d = start_date
        while d < end_date:
            all_vuls = db.session.query(
                func.count("*").label('counts')
            ).filter(
                and_(CobraResults.created_at >= d, CobraResults.created_at <= d + datetime.timedelta(1))
            ).all()
            vuls.append(all_vuls[0][0])
            labels.append(d.strftime("%Y%m%d"))
            d += datetime.timedelta(1)

        # get scan count
        d = start_date
        while d < end_date:
            t = int(time.mktime(d.timetuple()))
            all_scans = db.session.query(
                func.count("*").label("counts")
            ).filter(
                and_(CobraTaskInfo.time_start >= t, CobraTaskInfo.time_start <= t + 3600 * 24)
            ).all()
            scans.append(all_scans[0][0])
            d += datetime.timedelta(1)

        return jsonify(labels=labels, vuls=vuls, scans=scans)

    else:
        start_time_stamp = request.form.get("start_time_stamp")[:10]
        end_time_stamp = request.form.get("end_time_stamp")[:10]

        labels = list()
        vuls = list()
        scans = list()

        start_date = datetime.datetime.fromtimestamp(int(start_time_stamp[:10]))
        end_date = datetime.datetime.fromtimestamp(int(end_time_stamp[:10]))

        # get vulns count
        d = start_date
        while d < end_date:
            t = end_date if d + datetime.timedelta(1) > end_date else d + datetime.timedelta(1)

            all_vuls = db.session.query(
                func.count("*").label('counts')
            ).filter(
                and_(CobraResults.created_at >= d, CobraResults.created_at <= t)
            ).all()

            labels.append(d.strftime("%Y%m%d"))
            vuls.append(all_vuls[0][0])
            d += datetime.timedelta(1)

        # get scans count
        d = start_date
        while d < end_date:
            t_end_date = end_date if d + datetime.timedelta(1) > end_date else d + datetime.timedelta(1)
            t_start_date = time.mktime(d.timetuple())
            t_end_date = time.mktime(t_end_date.timetuple())

            all_scans = db.session.query(
                func.count("*").label("counts")
            ).filter(
                and_(CobraTaskInfo.time_start >= t_start_date, CobraTaskInfo.time_start <= t_end_date)
            ).all()
            scans.append(all_scans[0][0])
            d += datetime.timedelta(1)

        return jsonify(labels=labels, vuls=vuls, scans=scans)
