# -*- coding: utf-8 -*-

"""
    backend.projects
    ~~~~~~~~~~~~~~~~

    Implements projects controller

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time

from flask import render_template, request, jsonify, redirect

from . import ADMIN_URL
from utils import config
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass, login_required
from app.models import CobraProjects

__author__ = "lightless"
__email__ = "root@lightless.me"


# show all projects
@web.route(ADMIN_URL + '/projects/', methods=['GET'], defaults={'keyword': '0', 'page': 1})
@web.route(ADMIN_URL + '/projects/<int:page>', methods=['GET'], defaults={'keyword': '0'})
@web.route(ADMIN_URL + '/projects/<int:page>/<keyword>', methods=['GET'])
@login_required
def projects(page, keyword):
    if keyword != '0':
        filter_group = (CobraProjects.repository.like("%{}%".format(keyword)))
    else:
        filter_group = (CobraProjects.id > 0)
    per_page = 10
    projects = CobraProjects.query.filter(filter_group).order_by(CobraProjects.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraProjects.query.filter(filter_group).count()
    for project in projects:
        project.report = 'http://' + config.Config('cobra', 'domain').value + '/report/' + str(project.id)
    if keyword == '0':
        keyword = ''
    data = {
        'projects': projects,
        'page': page,
        'total': total,
        'keyword': keyword
    }
    return render_template("backend/project/projects.html", data=data)


# del the special projects
@web.route(ADMIN_URL + '/projects/del/', methods=['POST'])
@login_required
def del_project():
    if request.method == 'POST':

        vc = ValidateClass(request, "id")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        project_id = vc.vars.id
        project = CobraProjects.query.filter_by(id=project_id).first()
        try:
            db.session.delete(project)
            db.session.commit()
            return jsonify(code=1001, message='delete success.')
        except:
            return jsonify(code=4004, message='unknown error. please try later?')
    else:
        return 'Method error!'


@web.route(ADMIN_URL + '/projects/add/', methods=['GET', 'POST'])
def add_project():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')
    if request.method == "POST":
        vc = ValidateClass(request, "name", "repository", "url", "author", "pe", "remark", 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        project = CobraProjects(vc.vars.repository, vc.vars.url, vc.vars.name, vc.vars.author, '', vc.vars.pe, vc.vars.remark, vc.vars.status, current_time)
        try:
            db.session.add(project)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='Unknown error.')
    else:
        data = {
            'title': 'Create project',
            'type': 'add',
            'project': dict()
        }
        return render_template('backend/project/edit.html', data=data)


# edit the special projects
@web.route(ADMIN_URL + '/projects/edit/<int:project_id>', methods=['GET', 'POST'])
@login_required
def edit_project(project_id):
    if request.method == "POST":

        vc = ValidateClass(request, "id", "name", "repository", "url", "author", "pe", "remark", 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4004, message=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        project = CobraProjects.query.filter_by(id=project_id).first()
        if not project:
            return jsonify(code=4004, message='wrong project id.')

        # update project data
        project.name = vc.vars.name
        project.author = vc.vars.author
        project.pe = vc.vars.pe
        project.remark = vc.vars.remark
        project.status = vc.vars.status
        project.url = vc.vars.url
        project.repository = vc.vars.repository
        project.updated_at = current_time
        try:
            db.session.add(project)
            db.session.commit()
            return jsonify(code=1001, message='save success.')
        except:
            return jsonify(code=4004, message='Unknown error.')
    else:
        project = CobraProjects.query.filter_by(id=project_id).first()
        return render_template('backend/project/edit.html', data={
            'title': 'Edit project',
            'type': 'edit',
            'project': project,
            'id': project_id
        })
