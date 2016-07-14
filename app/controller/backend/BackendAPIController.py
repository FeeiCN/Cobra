#!/usr/bin/env python2
# coding: utf-8
# file: BackendAPIController.py

from flask import redirect

from . import ADMIN_URL
from app import web
from app.CommonClass.ValidateClass import ValidateClass
from app.models import CobraRules, CobraVuls, CobraProjects
from app.models import CobraWhiteList, CobraTaskInfo, CobraLanguages

__author__ = "lightless"
__email__ = "root@lightless.me"


# api: get all rules count
@web.route(ADMIN_URL + '/all_rules_count', methods=['GET'])
def all_rules_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    rules_count = CobraRules.query.count()
    return str(rules_count)


# api: get all vuls count
@web.route(ADMIN_URL + '/all_vuls_count', methods=['GET'])
def all_vuls_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    vuls_count = CobraVuls.query.count()
    return str(vuls_count)


# api: get all projects count
@web.route(ADMIN_URL + '/all_projects_count', methods=['GET'])
def all_projects_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    projects_count = CobraProjects.query.count()
    return str(projects_count)


# api: get all whitelists count
@web.route(ADMIN_URL + '/all_whitelists_count', methods=['GET'])
def all_whitelists_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    whitelists_count = CobraWhiteList.query.count()
    return str(whitelists_count)


# api: get all tasks count
@web.route(ADMIN_URL + '/all_tasks_count', methods=['GET'])
def all_tasks_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    tasks_count = CobraTaskInfo.query.count()
    return str(tasks_count)


# api: get all languages count
@web.route(ADMIN_URL + '/all_languages_count', methods=['GET'])
def all_languages_count():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    languages_count = CobraLanguages.query.count()
    return str(languages_count)

