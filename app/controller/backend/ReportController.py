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
import time

from flask import render_template, request, jsonify, redirect

from . import ADMIN_URL
import os
from app import web
from app.CommonClass.ValidateClass import login_required
from app.models import CobraProjects, CobraResults
from pickup.git import Git
from utils import config, common


@web.route(ADMIN_URL + '/report/', methods=['GET'])
@login_required
def report(page):
    projects = CobraProjects.query.order_by(CobraProjects.id.asc()).all()
    rank = []
    offline = []
    for project in projects:
        hard_coded_password_rule_ids = [137, 135, 134, 133, 132, 130, 129, 124, 123, 122]
        count_total = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(hard_coded_password_rule_ids)).count()

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
            count_fixed = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(hard_coded_password_rule_ids), CobraResults.status == 2).count()
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
            if s['remark'] == 'offline':
                offline.append(s)
            else:
                rank.append(s)
    rank = sorted(rank, key=lambda x: x['not_fixed'], reverse=True)
    for r in rank:
        print("| [{0}](http://cobra.meili-inc.com/report/{1}) | {6} | {2} | {3} | {4} | {5} |".format(r['name'], r['id'], r['not_fixed'], r['fixed'], r['total'], r['remark'], r['author']))
    for r in offline:
        print("| [{0}](http://cobra.meili-inc.com/report/{1}) | {6} | {2} | {3} | {4} | {5} |".format(r['name'], r['id'], r['not_fixed'], r['fixed'], r['total'], r['remark'], r['author']))
    data = {
        'projects': projects,
        'page': page
    }
    return render_template("backend/report/report.html", data=data)
