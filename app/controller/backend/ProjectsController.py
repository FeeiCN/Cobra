#!/usr/bin/env python2
# coding: utf-8
# file: ProjectsController.py

import time

from flask import redirect, render_template, request, jsonify

from . import ADMIN_URL
from app import web, db
from app.CommonClass.ValidateClass import ValidateClass
from app.models import CobraProjects


__author__ = "lightless"
__email__ = "root@lightless.me"


# show all projects
@web.route(ADMIN_URL + '/projects/<int:page>', methods=['GET'])
def projects(page):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page = 10
    project = CobraProjects.query.order_by('id desc').limit(per_page).offset((page - 1) * per_page).all()
    data = {
        'projects': project,
    }
    return render_template("backend/project/projects.html", data=data)


# del the special projects
@web.route(ADMIN_URL + '/del_project', methods=['POST'])
def del_project():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

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
            return jsonify(tag='success', msg='delete success.')
        except:
            return jsonify(tag='danger', msg='unknown error. please try later?')
    else:
        return 'Method error!'


# edit the special projects
@web.route(ADMIN_URL + '/edit_project/<int:project_id>', methods=['GET', 'POST'])
def edit_project(project_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":

        vc = ValidateClass(request, "project_id", "name", "repository", "author", "remark")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        project = CobraProjects.query.filter_by(id=project_id).first()
        if not project:
            return jsonify(tag='danger', msg='wrong project id.')

        # update project data
        project.name = vc.vars.name
        project.author = vc.vars.author
        project.remark = vc.vars.remark
        project.repository = vc.vars.repository
        project.updated_at = current_time
        try:
            db.session.add(project)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='Unknown error.')
    else:
        project = CobraProjects.query.filter_by(id=project_id).first()
        return render_template('backend/project/edit_project.html', data={
            'project': project
        })

