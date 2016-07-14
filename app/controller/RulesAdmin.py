#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import datetime
import time

from flask import render_template, request, jsonify, session, escape, redirect
from sqlalchemy.sql import func, and_

from app import CobraProjects, CobraWhiteList, CobraAdminUser
from app import CobraTaskInfo, CobraResults
from app import web, CobraRules, CobraVuls, db, CobraLanguages
from app.CommonClass.ValidateClass import ValidateClass

# default admin url
ADMIN_URL = '/admin'


# login page and index
@web.route(ADMIN_URL + '/', methods=['GET'])
@web.route(ADMIN_URL + '/index', methods=['GET', 'POST'])
def index():

    if ValidateClass.check_login():
        return redirect(ADMIN_URL + '/main')

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

            return "Login success, jumping...<br /><script>window.setTimeout(\"location='main'\", 1000);</script>"
    else:
        return render_template("rulesadmin/index.html")


# main view
@web.route(ADMIN_URL + '/main', methods=['GET'])
def main():
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + "/index")
    else:
        return render_template("rulesadmin/main.html")


# all rules button
@web.route(ADMIN_URL + '/rules/<int:page>', methods=['GET'])
def rules(page):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page = 10
    cobra_rules = CobraRules.query.order_by('id').limit(per_page).offset((page-1)*per_page).all()
    cobra_vuls = CobraVuls.query.all()
    cobra_lang = CobraLanguages.query.all()
    all_vuls = {}
    all_language = {}
    all_level = {1: 'Low', 2: 'Medium', 3: 'High'}
    for vul in cobra_vuls:
        all_vuls[vul.id] = vul.name
    for lang in cobra_lang:
        all_language[lang.id] = lang.language

    # replace id with real name
    for rule in cobra_rules:
        try:
            rule.vul_id = all_vuls[rule.vul_id]
        except KeyError:
            rule.vul_id = 'Unknown Type'

        try:
            rule.language = all_language[rule.language]
        except KeyError:
            rule.language = 'Unknown Language'

        try:
            rule.level = all_level[rule.level]
        except KeyError:
            rule.level = 'Unknown Level'

    data = {
        # 'paginate': cobra_rules,
        'rules': cobra_rules,
    }

    return render_template('rulesadmin/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/add_new_rule', methods=['GET', 'POST'])
def add_new_rule():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        vc = ValidateClass(request, 'vul_type', 'language', 'regex', 'regex_confirm',
                           'description', 'repair', 'level')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        rule = CobraRules(vc.vars.vul_type, vc.vars.language, vc.vars.regex, vc.vars.regex_confirm,
                          vc.vars.description, vc.vars.repair, 1, vc.vars.level, current_time, current_time)
        try:
            db.session.add(rule)
            db.session.commit()
            return jsonify(tag='success', msg='add success.')
        except:
            return jsonify(tag='danger', msg='add failed, try again later?')
    else:
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        data = {
            'vul_type': vul_type,
            'languages': languages
        }
        return render_template('rulesadmin/add_new_rule.html', data=data)


# del special rule
@web.route(ADMIN_URL + '/del_rule', methods=['POST'])
def del_rule():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    vc = ValidateClass(request, "rule_id")
    vc.check_args()
    vul_id = vc.vars.rule_id
    if vul_id:
        r = CobraRules.query.filter_by(id=vul_id).first()
        try:
            db.session.delete(r)
            db.session.commit()
            return jsonify(tag='success', msg='delete success.')
        except:
            return jsonify(tag='danger', msg='delete failed. Try again later?')
    else:
        return jsonify(tag='danger', msg='wrong id')


# edit special rule
@web.route(ADMIN_URL + '/edit_rule/<int:rule_id>', methods=['GET', 'POST'])
def edit_rule(rule_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "vul_type", "language", "regex", "regex_confirm", "description", "rule_id",
                           "repair", "status", "level")
        ret, msg = vc.check_args()

        if not ret:
            return jsonify(tag="danger", msg=msg)

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vc.vars.vul_type
        r.language = vc.vars.language
        r.regex = vc.vars.regex
        r.regex_confirm = vc.vars.regex_confirm
        r.description = vc.vars.description
        r.repair = vc.vars.repair
        r.status = vc.vars.status
        r.level = vc.vars.level
        r.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
        try:
            db.session.add(r)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        r = CobraRules.query.filter_by(id=rule_id).first()
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        return render_template('rulesadmin/edit_rule.html', data={
            'rule': r,
            'all_vuls': vul_type,
            'all_lang': languages,
        })


# add new vuls button
@web.route(ADMIN_URL + '/add_new_vul', methods=['GET', 'POST'])
def add_new_vul():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "name", "description", "repair")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        vul = CobraVuls(vc.vars.name, vc.vars.description, vc.vars.repair, current_time, current_time)
        try:
            db.session.add(vul)
            db.session.commit()
            return jsonify(tag='success', msg='Add Success.')
        except:
            return jsonify(tag='danger', msg='Add failed. Please try again later.')
    else:
        return render_template('rulesadmin/add_new_vul.html')


# show all vuls click
@web.route(ADMIN_URL + '/vuls/<int:page>', methods=['GET'])
def vuls(page):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page_vuls = 10
    all_vuls = CobraVuls.query.order_by('id').limit(per_page_vuls).offset((page-1)*per_page_vuls).all()
    data = {
        'vuls': all_vuls
    }
    return render_template('rulesadmin/vuls.html', data=data)


# del special vul
@web.route(ADMIN_URL + '/del_vul', methods=['POST'])
def del_vul():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    vc = ValidateClass(request, "vul_id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    if vc.vars.vul_id:
        v = CobraVuls.query.filter_by(id=vc.vars.vul_id).first()
        try:
            db.session.delete(v)
            db.session.commit()
            return jsonify(tag='success', msg='delete success.')
        except:
            return jsonify(tag='danger', msg='delete failed. Try again later?')
    else:
        return jsonify(tag='danger', msg='wrong id')


# edit special vul
@web.route(ADMIN_URL + '/edit_vul/<int:vul_id>', methods=['GET', 'POST'])
def edit_vul(vul_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "name", "description", "repair")
        ret, msg = vc.check_args()

        if not ret:
            return jsonify(tag="danger", msg=msg)

        v = CobraVuls.query.filter_by(id=vul_id).first()
        v.name = vc.args.name
        v.description = vc.args.description
        v.repair = vc.args.repair

        try:
            db.session.add(v)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        v = CobraVuls.query.filter_by(id=vul_id).first()
        return render_template('rulesadmin/edit_vul.html', data={
            'vul': v,
        })


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


# show all projects
@web.route(ADMIN_URL + '/projects/<int:page>', methods=['GET'])
def projects(page):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page = 10
    project = CobraProjects.query.order_by('id').limit(per_page).offset((page - 1) * per_page).all()
    data = {
        'projects': project,
    }
    return render_template("rulesadmin/projects.html", data=data)


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
        return render_template('rulesadmin/edit_project.html', data={
            'project': project
        })


# show all white lists
@web.route(ADMIN_URL + '/whitelists/<int:page>', methods=['GET'])
def whitelists(page):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page = 10
    whitelists = CobraWhiteList.query.order_by('id').limit(per_page).offset((page - 1) * per_page).all()
    data = {
        'whitelists': whitelists,
    }
    return render_template('rulesadmin/whitelists.html', data=data)


# add new white list
@web.route(ADMIN_URL + '/add_whitelist', methods=['GET', 'POST'])
def add_whitelist():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "project_id", "rule_id", "path", "reason")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if vc.vars.path[0] != '/':
            vc.vars.path = '/' + vc.vars.path
        whitelist = CobraWhiteList(vc.vars.project_id, vc.vars.rule_id, vc.vars.path, vc.vars.reason,
                                   1, current_time, current_time)
        try:
            db.session.add(whitelist)
            db.session.commit()
            return jsonify(tag='success', msg='add success.')
        except:
            return jsonify(tag='danger', msg='unknown error. Try again later?')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        data = {
            'rules': rules,
            'projects': projects,
        }
        return render_template('rulesadmin/add_new_whitelist.html', data=data)


# del the special white list
@web.route(ADMIN_URL + '/del_whitelist', methods=['POST'])
def del_whitelist():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    vc = ValidateClass(request, "whitelist_id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    whitelist = CobraWhiteList.query.filter_by(id=vc.vars.whitelist_id).first()
    try:
        db.session.delete(whitelist)
        db.session.commit()
        return jsonify(tag='success', msg='delete success.')
    except:
        return jsonify(tag='danger', msg='unknown error.')


# edit the special white list
@web.route(ADMIN_URL + '/edit_whitelist/<int:whitelist_id>', methods=['GET', 'POST'])
def edit_whitelist(whitelist_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "whitelist_id", "project", "rule", "path", "reason", "status")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
        if not whitelist:
            return jsonify(tag='danger', msg='wrong whitelist')

        whitelist.project_id = vc.vars.project_id
        whitelist.rule_id = vc.vars.rule_id
        whitelist.path = vc.vars.path
        whitelist.reason = vc.vars.reason
        whitelist.status = vc.vars.status

        try:
            db.session.add(whitelist)
            db.session.commit()
            return jsonify(tag='success', msg='update success.')
        except:
            return jsonify(tag='danger', msg='unknown error.')
    else:
        rules = CobraRules.query.all()
        projects = CobraProjects.query.all()
        whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
        data = {
            'rules': rules,
            'projects': projects,
            'whitelist': whitelist,
        }

        return render_template('rulesadmin/edit_whitelist.html', data=data)


# show all tasks
@web.route(ADMIN_URL + '/tasks/<int:page>', methods=['GET'])
def tasks(page):
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    per_page = 10
    tasks = CobraTaskInfo.query.order_by('id').limit(per_page).offset((page - 1) * per_page).all()

    # replace data
    for task in tasks:
        task.scan_way = "Full Scan" if task.scan_way == 1 else "Diff Scan"
    data = {
        'tasks': tasks,
    }
    return render_template('rulesadmin/tasks.html', data=data)


# del the special task
@web.route(ADMIN_URL + '/del_task', methods=['POST'])
def del_task():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    task = CobraTaskInfo.query.filter_by(id=vc.vars.task_id).first()
    try:
        db.session.delete(task)
        db.session.commit()
        return jsonify(tag='success', msg='delete success.')
    except:
        return jsonify(tag='danger', msg='unknown error.')


# edit the special task
@web.route(ADMIN_URL + '/edit_task/<int:task_id>', methods=['GET', 'POST'])
def edit_task(task_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        # vc = ValidateClass(request, "branch", "scan_way", "new_version", "old_version", "target")
        # ret, msg = vc.check_args()
        # if not ret:
        #     return jsonify(tag="danger", msg=msg)
        # TODO: check new_version and old_version when scan_way == 2
        branch = request.form.get('branch')
        scan_way = request.form.get('scan_way')
        new_version = request.form.get('new_version')
        old_version = request.form.get('old_version')
        target = request.form.get('target')

        if not branch or branch == "":
            return jsonify(tag='danger', msg='branch can not be empty')
        if not scan_way or scan_way == "":
            return jsonify(tag='danger', msg='scan way can not be empty')
        if (scan_way == 2) and ((not new_version or new_version == "") or (not old_version or old_version == "")):
            return jsonify(tag='danger', msg='In diff scan mode, new version and old version can not be empty')
        if not target or target == "":
            return jsonify(tag='danger', msg='Target can not be empty.')

        task = CobraTaskInfo.query.filter_by(id=task_id).first()
        task.branch = branch
        task.scan_way = scan_way
        task.new_version = new_version
        task.old_version = old_version
        task.target = target
        task.updated_time = datetime.datetime.now()

        try:
            db.session.add(task)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        task = CobraTaskInfo.query.filter_by(id=task_id).first()
        return render_template('rulesadmin/edit_task.html', data={
            'task': task,
        })


# search_rules_bar
@web.route(ADMIN_URL + '/search_rules_bar', methods=['GET'])
def search_rules_bar():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    languages = CobraLanguages.query.all()
    vuls = CobraVuls.query.all()

    data = {
        'languages': languages,
        'vuls': vuls,
    }

    return render_template('rulesadmin/search_rules_bar.html', data=data)


# search rules
@web.route(ADMIN_URL + '/search_rules', methods=['POST'])
def search_rules():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':

        vc = ValidateClass(request, "language", "vul")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        rules = None

        if vc.vars.language == 'all' and vc.vars.vul == 'all':
            rules = CobraRules.query.all()
        elif vc.vars.language == 'all' and vc.vars.vul != 'all':
            rules = CobraRules.query.filter_by(vul_id=vc.vars.vul).all()
        elif vc.vars.language != 'all' and vc.vars.vul == 'all':
            rules = CobraRules.query.filter_by(language=vc.vars.language).all()
        elif vc.vars.language != 'all' and vc.vars.vul != 'all':
            rules = CobraRules.query.filter_by(language=vc.vars.language, vul_id=vc.vars.vul).all()
        else:
            return 'error!'

        cobra_vuls = CobraVuls.query.all()
        cobra_lang = CobraLanguages.query.all()
        all_vuls = {}
        all_language = {}
        for vul in cobra_vuls:
            all_vuls[vul.id] = vul.name
        for lang in cobra_lang:
            all_language[lang.id] = lang.language

        # replace id with real name
        for rule in rules:
            try:
                rule.vul_id = all_vuls[rule.vul_id]
            except KeyError:
                rule.vul_id = 'Unknown Type'
            try:
                rule.language = all_language[rule.language]
            except KeyError:
                rule.language = 'Unknown Language'

        data = {
            'rules': rules,
        }

        return render_template('rulesadmin/rules.html', data=data)


@web.route(ADMIN_URL + "/add_new_language", methods=['GET', 'POST'])
def add_new_language():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":

        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        l = CobraLanguages(vc.vars.language, vc.vars.extensions)
        try:
            db.session.add(l)
            db.session.commit()
            return jsonify(tag="success", msg="add success")
        except:
            return jsonify(tag="danger", msg="try again later?")
    else:
        return render_template("rulesadmin/add_new_language.html")


@web.route(ADMIN_URL + "/languages", methods=['GET'])
def languages():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + "/index")

    languages = CobraLanguages.query.all()
    data = {
        'languages': languages,
    }
    return render_template("rulesadmin/languages.html", data=data)


@web.route(ADMIN_URL + "/del_language", methods=['POST'])
def del_language():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + "/index")

    vc = ValidateClass(request, "id")
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(tag="danger", msg=msg)

    l = CobraLanguages.query.filter_by(id=vc.vars.id).first()
    try:
        db.session.delete(l)
        db.session.commit()
        return jsonify(tag="success", msg="delete success.")
    except:
        return jsonify(tag="danger", msg="delete failed.")


@web.route(ADMIN_URL + "/edit_language/<int:language_id>", methods=['POST', 'GET'])
def edit_language(language_id):

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + "/index")

    if request.method == "POST":

        vc = ValidateClass(request, "language", "extensions")
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(tag="danger", msg=msg)

        l = CobraLanguages.query.filter_by(id=language_id).first()
        try:
            l.language = vc.vars.language
            l.extensions = vc.vars.extensions
            db.session.add(l)
            db.session.commit()
            return jsonify(tag="success", msg="update success.")
        except:
            return jsonify(tag="danger", msg="try again later?")

    else:
        l = CobraLanguages.query.filter_by(id=language_id).first()
        data = {
            'language': l,
        }
        return render_template("rulesadmin/edit_language.html", data=data)


@web.route(ADMIN_URL + "/dashboard", methods=['GET'])
def dashboard():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    cobra_rules = db.session.query(CobraRules.id, CobraRules.vul_id,).all()
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
        all_cobra_vuls[x.id] = x.name   # vul_id -> vul_name

    total_vuls = []
    for x in all_vuls:      # all_vuls: results group by rule_id and count(*)
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
    return render_template("rulesadmin/dashboard.html", data=data)


@web.route(ADMIN_URL + "/get_scan_information", methods=['POST'])
def get_scan_information():

    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":
        start_time = request.form.get("start_time")
        end_time = request.form.get("end_time")
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
    hit_rules = None

    if show_all:
        hit_rules = db.session.query(CobraResults.rule_id).all()
    else:
        start_time_stamp = request.form.get("start_time_stamp")
        end_time_stamp = request.form.get("end_time_stamp")
        start_time = datetime.datetime.fromtimestamp(int(start_time_stamp[:10]))
        end_time = datetime.datetime.fromtimestamp(int(end_time_stamp[:10]))
        hit_rules = db.session.query(CobraResults.rule_id).filter(
            and_(CobraResults.created_at >= start_time, CobraResults.created_at <= end_time)
        ).all()

    for rule_id in hit_rules:
        language_id = db.session.query(CobraRules.language).filter_by(id=int(rule_id[0])).all()
        language_id = int(language_id[0][0])
        language_name = db.session.query(
            CobraLanguages.language, CobraLanguages.extensions
        ).filter_by(id=language_id).all()
        language_name = language_name[0]
        if return_value.get(language_name[0]):
            return_value[language_name[0]] += 1
        else:
            return_value[language_name[0]] = 1
    return jsonify(data=return_value)


@web.route(ADMIN_URL + "/graph_lines", methods=['POST'])
def graph_lines():
    # everyday vulns count
    # everyday scan count
    if not ValidateClass.check_login():
        return redirect(ADMIN_URL + '/index')
    show_all = request.form.get("show_all")
    if show_all:
        days = 15-1
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
                and_(CobraTaskInfo.time_start >= t, CobraTaskInfo.time_start <= t + 3600*24)
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

