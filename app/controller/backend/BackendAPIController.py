# -*- coding: utf-8 -*-

"""
    backend.api
    ~~~~~~~~~~~

    Implements api

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""

from . import ADMIN_URL
from app import web
from app.models import CobraRules, CobraVuls, CobraProjects
from app.models import CobraWhiteList, CobraTaskInfo, CobraLanguages
from app.CommonClass.ValidateClass import login_required

__author__ = "lightless"
__email__ = "root@lightless.me"


# api: get all rules count
@web.route(ADMIN_URL + '/all_rules_count', methods=['GET'])
@login_required
def all_rules_count():

    rules_count = CobraRules.query.count()
    return str(rules_count)


# api: get all vuls count
@web.route(ADMIN_URL + '/all_vuls_count', methods=['GET'])
@login_required
def all_vuls_count():

    vuls_count = CobraVuls.query.count()
    return str(vuls_count)


# api: get all projects count
@web.route(ADMIN_URL + '/all_projects_count', methods=['GET'])
@login_required
def all_projects_count():

    projects_count = CobraProjects.query.count()
    return str(projects_count)


# api: get all whitelists count
@web.route(ADMIN_URL + '/all_whitelists_count', methods=['GET'])
@login_required
def all_whitelists_count():

    whitelists_count = CobraWhiteList.query.count()
    return str(whitelists_count)


# api: get all tasks count
@web.route(ADMIN_URL + '/all_tasks_count', methods=['GET'])
@login_required
def all_tasks_count():

    tasks_count = CobraTaskInfo.query.count()
    return str(tasks_count)


# api: get all languages count
@web.route(ADMIN_URL + '/all_languages_count', methods=['GET'])
@login_required
def all_languages_count():

    languages_count = CobraLanguages.query.count()
    return str(languages_count)

