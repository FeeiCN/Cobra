# -*- coding: utf-8 -*-

"""
    backend.result
    ~~~~~~~~~~~~~~

    Implements result controller

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""

from . import ADMIN_URL
from utils import config
from app import web, db
from utils.validate import login_required
from flask import render_template
from app.models import CobraResults, CobraVuls, CobraRules, CobraProjects
from sqlalchemy import func, and_


@web.route(ADMIN_URL + '/result/', methods=['GET'], defaults={'pid': 0, 'page': 1, 'vt_id': 0, 'rid': 0})
@web.route(ADMIN_URL + '/result/<int:page>', methods=['GET'], defaults={'pid': 0, 'vt_id': 0, 'rid': 0})
@web.route(ADMIN_URL + '/result/<int:page>/<int:pid>', methods=['GET'], defaults={'vt_id': 0, 'rid': 0})
@web.route(ADMIN_URL + '/result/<int:page>/<int:pid>/<int:vt_id>', methods=['GET'], defaults={'rid': 0})
@web.route(ADMIN_URL + '/result/<int:page>/<int:pid>/<int:vt_id>/<int:rid>', methods=['GET'])
@login_required
def result(pid, page, vt_id, rid):
    pid = int(pid)
    page = int(page)
    vt_id = int(vt_id)
    rid = int(rid)
    if pid != 0:
        filter_group = (CobraResults.project_id == pid,)
    else:
        filter_group = (CobraResults.project_id > 0,)
    result_filter = filter_group
    if rid != 0:
        result_filter = result_filter + (CobraResults.rule_id == rid,)

    result_filter = result_filter + (CobraResults.rule_id == CobraRules.id,)
    per_page = 10
    results = db.session.query(
        CobraResults.rule_id,
        CobraResults.status,
        CobraResults.project_id,
        CobraResults.updated_at,
        CobraResults.file,
        CobraResults.line,
        CobraResults.id,
        CobraRules.description
    ).filter(*result_filter).order_by(CobraResults.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraResults.query.filter(*result_filter).count()

    # Not fixed vulnerability types
    filter = filter_group + (CobraResults.rule_id == CobraRules.id, CobraVuls.id == CobraRules.vul_id,)
    showed_vul_type = db.session.query(
        func.count().label("showed_vul_number"), CobraVuls.name, CobraVuls.id
    ).filter(
        and_(*filter)
    ).group_by(CobraVuls.name, CobraVuls.id).all()

    # Not fixed vulnerability rules types
    showed_rule_type = db.session.query(CobraRules.description, CobraRules.id, CobraRules.vul_id).filter(
        and_(*filter)
    ).group_by(CobraRules.id).all()

    # For frontpage filter
    select_vul_type = list()
    # Every vulnerability count
    for r in showed_vul_type:
        select_vul_type.append([r[1], r[2], r[0]])
    select_rule_type = list()
    for r in showed_rule_type:
        select_rule_type.append([r[0], r[1], r[2]])

    vulnerability_types = {}
    for v in select_vul_type:
        vulnerability_types[v[1]] = {
            'id': v[1],
            'name': v[0],
            'count': v[2],
            'rules': []
        }
        for r in select_rule_type:
            if r[2] == v[1]:
                vulnerability_types[v[1]]['rules'].append({
                    'id': r[1],
                    'name': r[0]
                })

    projects = CobraProjects.query.filter(CobraProjects.status > 0).all()
    data = {
        'vulnerability_types': vulnerability_types,
        'projects': projects,
        'results': results,
        'page': page,
        'pid': pid,
        'vt_id': vt_id,
        'rid': rid,
        'total': total,
        'domain': config.Config('cobra', 'domain').value
    }
    return render_template("backend/result/result.html", data=data)
