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
from flask import render_template, request, jsonify, redirect

from . import ADMIN_URL
import os
from app import web
from app.CommonClass.ValidateClass import login_required
from app.models import CobraProjects, CobraResults, CobraRules, CobraVuls
from pickup.git import Git
from utils import config, common


@web.route(ADMIN_URL + '/report/', methods=['GET'], defaults={'vid': 0})
@web.route(ADMIN_URL + '/report/<int:vid>', methods=['GET'])
@login_required
def reports(vid):
    projects = CobraProjects.query.order_by(CobraProjects.id.asc()).all()
    rank = []
    offline = []
    for project in projects:
        special_rules_ids = []
        if vid is 0:
            count_total = CobraResults.query.filter(CobraResults.project_id == project.id).count()
        else:
            rules = CobraRules.query.with_entities(CobraResults.id).filter(CobraRules.vul_id == vid).all()
            for rule in rules:
                special_rules_ids.append(rule.id)
            count_total = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(special_rules_ids)).count()

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
                count_fixed = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.status == 2).count()
            else:
                count_fixed = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(special_rules_ids), CobraResults.status == 2).count()
            count_not_fixed = count_total - count_fixed
            remark = ''
        else:
            count_fixed = 0
            count_not_fixed = 0
            remark = 'offline'
        if count_total != 0:
            s = {
                'name': project.name,
                'id': project.id,
                'not_fixed': count_not_fixed,
                'fixed': count_fixed,
                'total': count_total,
                'remark': remark,
                'author': project.author
            }
            rank.append(s)
    rank = sorted(rank, key=lambda x: x['not_fixed'], reverse=True)
    vulnerabilities_types = CobraVuls.query.all()
    data = {
        'rank': rank,
        'vulnerabilities_types': vulnerabilities_types,
        'vid': vid
    }
    return render_template("backend/report/report.html", data=data)
