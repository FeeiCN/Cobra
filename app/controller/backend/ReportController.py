# -*- coding: utf-8 -*-

"""
    backend.report
    ~~~~~~~~~~~~~~

    Implements report controller

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
from flask import render_template

from . import ADMIN_URL
import os
from app import web
from app.CommonClass.ValidateClass import login_required
from app.models import CobraProjects, CobraResults, CobraRules, CobraVuls
from pickup.git import Git
from utils import config, common


@web.route(ADMIN_URL + '/report/', methods=['GET'], defaults={'vid': 0, 'start_time': '0', 'end_time': '0'})
@web.route(ADMIN_URL + '/report/<int:vid>', methods=['GET'], defaults={'start_time': '0', 'end_time': '0'})
@web.route(ADMIN_URL + '/report/<int:vid>/<start_time>/<end_time>', methods=['GET'])
@login_required
def reports(vid, start_time, end_time):
    projects = CobraProjects.query.order_by(CobraProjects.id.asc()).all()
    rank = []
    count_project_not_fixed = 0
    count_project_fixed = 0
    count_vulnerability_not_fixed = 0
    count_vulnerability_fixed = 0

    special_rules_ids = []
    if vid is 0:
        vulnerability_fixed_week = CobraResults.query.with_entities(CobraResults.id).filter(CobraResults.updated_at > '2016-11-28 00:00:00', CobraResults.updated_at < '2016-11-04 23:59:59', CobraResults.status == 2).count()
        vulnerability_not_fixed_week = CobraResults.query.with_entities(CobraResults.id).filter(CobraResults.updated_at > '2016-11-28 00:00:00', CobraResults.updated_at < '2016-11-04 23:59:59', CobraResults.status < 2).count()
    else:
        rules = CobraRules.query.with_entities(CobraRules.id).filter(CobraRules.vul_id == vid).all()
        for rule in rules:
            special_rules_ids.append(rule.id)
        vulnerability_fixed_week = CobraResults.query.filter(CobraResults.rule_id.in_(special_rules_ids), CobraResults.created_at > '2016-11-28 00:00:00', CobraResults.created_at < '2016-11-04 23:59:59', CobraResults.status == 2).count()
        vulnerability_not_fixed_week = CobraResults.query.with_entities(CobraResults.id).filter(CobraResults.updated_at > '2016-11-28 00:00:00', CobraResults.updated_at < '2016-11-04 23:59:59', CobraResults.status < 2).count()

    filter_group = (CobraResults.created_at > '{0} 00:00:00'.format(start_time), CobraResults.created_at < '{0} 23:59:59'.format(end_time),)
    for project in projects:
        if vid is 0:
            filter_group_total_base = (CobraResults.project_id == project.id,)
            if start_time == '0' and end_time == '0':
                filter_group_total = filter_group_total_base + ()
                count_total = CobraResults.query.filter(*filter_group_total).count()
            else:
                filter_group_total = filter_group + filter_group_total_base + ()
                count_total = CobraResults.query.filter(*filter_group_total).count()
        else:
            filter_group_total_base = (CobraResults.project_id == project.id, CobraResults.rule_id.in_(special_rules_ids),)
            if start_time == '0' and end_time == '0':
                filter_group_total = filter_group_total_base + ()
                count_total = CobraResults.query.filter(*filter_group_total).count()
            else:
                filter_group_total = filter_group + filter_group_total_base + ()
                count_total = CobraResults.query.filter(*filter_group_total).count()

        # detect project Cobra configuration file
        if project.repository[0] == '/':
            project_directory = project.repository
        else:
            project_directory = Git(project.repository).repo_directory
        cobra_properties = config.properties(os.path.join(project_directory, 'cobra'))
        need_scan = True
        if 'scan' in cobra_properties:
            need_scan = common.to_bool(cobra_properties['scan'])
        if need_scan:
            if vid is 0:
                filter_group_fixed_base = (CobraResults.project_id == project.id, CobraResults.status == 2,)
                if start_time == '0' and end_time == '0':
                    filter_group_fixed = filter_group_fixed_base + ()
                    count_fixed = CobraResults.query.filter(*filter_group_fixed).count()
                else:
                    filter_group_fixed = filter_group + filter_group_fixed_base + ()
                    count_fixed = CobraResults.query.filter(*filter_group_fixed).count()
            else:
                filter_group_fixed_base = (CobraResults.project_id == project.id, CobraResults.status == 2, CobraResults.rule_id.in_(special_rules_ids))
                if start_time == '0' and end_time == '0':
                    filter_group_fixed = filter_group_fixed_base + ()
                    count_fixed = CobraResults.query.filter(*filter_group_fixed).count()
                else:
                    filter_group_fixed = filter_group + filter_group_fixed_base + ()
                    count_fixed = CobraResults.query.filter(*filter_group_fixed).count()
            if project.status == 1:
                count_not_fixed = count_total - count_fixed
                remark = ''
            else:
                count_fixed = count_total
                count_not_fixed = 0
                remark = 'deleted'
        else:
            count_fixed = count_total
            count_not_fixed = 0
            remark = 'offline'
        if count_total != 0:
            if need_scan:
                if project.status == 1:
                    if count_not_fixed == 0:
                        count_project_fixed += 1
                        count_vulnerability_fixed += count_fixed
                        ret_whole = 'fixed'
                    else:
                        count_project_not_fixed += 1
                        count_vulnerability_fixed += count_fixed
                        count_vulnerability_not_fixed += count_not_fixed
                        ret_whole = 'not_fixed'
                else:
                    # deleted project
                    count_project_fixed += 1
                    count_vulnerability_fixed += count_fixed
                    ret_whole = 'fixed'
            else:
                count_project_fixed += 1
                count_vulnerability_fixed += count_fixed
                ret_whole = 'fixed'
            report = 'http://' + config.Config('cobra', 'domain').value + '/report/' + str(project.id)
            s = {
                'name': project.name,
                'id': project.id,
                'not_fixed': count_not_fixed,
                'fixed': count_fixed,
                'total': count_total,
                'remark': remark,
                'author': project.author,
                'report': report,
                'class': ret_whole
            }
            rank.append(s)
    rank = sorted(rank, key=lambda x: x['not_fixed'], reverse=True)
    vulnerabilities_types = CobraVuls.query.all()
    if start_time == '0':
        start_time = ''
    if end_time == '0':
        end_time = ''
    data = {
        'rank': rank,
        'vulnerabilities_types': vulnerabilities_types,
        'vid': vid,
        'count': {
            'vulnerability': {
                'not_fixed': count_vulnerability_not_fixed,
                'fixed': count_vulnerability_fixed,
                'total': count_vulnerability_not_fixed + count_vulnerability_fixed
            },
            'project': {
                'not_fixed': count_project_not_fixed,
                'fixed': count_project_fixed,
                'total': count_project_not_fixed + count_project_fixed
            },
            'week': {
                'fixed': "{0}({1})".format(vulnerability_fixed_week, common.percent(vulnerability_fixed_week, count_vulnerability_fixed)),
                'not_fixed': "{0}({1})".format(vulnerability_not_fixed_week, common.percent(vulnerability_not_fixed_week, count_vulnerability_not_fixed))
            }
        },
        'filter': {
            'start': start_time,
            'end': end_time
        }
    }
    return render_template("backend/report/report.html", data=data)
