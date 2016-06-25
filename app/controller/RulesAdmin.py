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
import time
import datetime

from flask import render_template, request, jsonify, session, escape, redirect
from sqlalchemy.sql import func, and_

from app import web, CobraRules, CobraVuls, db, CobraLanguages
from app import CobraProjects, CobraWhiteList, CobraAdminUser
from app import CobraTaskInfo, CobraResults

# default admin url
ADMIN_URL = '/admin'


# check login function
def is_login():
    if session.get('is_login') and session.get('is_login') == True:
        return True
    else:
        return False


@web.route(ADMIN_URL + '/', methods=['GET'])
@web.route(ADMIN_URL + '/index', methods=['GET', 'POST'])
def index():

    if is_login():
        return redirect(ADMIN_URL + '/main')

    if request.method == "POST":
        username = request.form.get('username')
        password = request.form.get('password')

        au = CobraAdminUser.query.filter_by(username=username).first()
        if not au or not au.verify_password(password):
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
    # check login
    if not is_login():
        return redirect(ADMIN_URL + '/index')
    else:
        return render_template("rulesadmin/main.html")


# all rules button
@web.route(ADMIN_URL + '/rules/<int:page>', methods=['GET'])
def rules(page):

    # check login
    if not is_login():
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        vul_type = request.form.get('vul_type')
        lang = request.form.get('language')
        regex = request.form.get('regex')
        regex_confirm = request.form.get('regex_confirm')
        description = request.form.get('description')
        repair = request.form.get('repair')
        level = request.form.get('level')

        if not vul_type or vul_type == "":
            return jsonify(tag='danger', msg='vul type error.')
        if not lang or lang == "":
            return jsonify(tag='danger', msg='language error.')
        if not regex or regex == "":
            return jsonify(tag='danger', msg='regex can not be blank')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be blank')
        if not regex_confirm or regex_confirm == "":
            return jsonify(tag='danger', msg='confirm regex can not be blank')
        if not repair or repair == "":
            return jsonify(tag='danger', msg='repair can not be empty')
        if not level or level == "":
            return jsonify(tag='danger', msg='repair can not be blank.')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        rule = CobraRules(vul_type, lang, regex, regex_confirm, description, repair,
                          1, level, current_time, current_time)
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    vul_id = request.form['rule_id']
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        vul_type = request.form.get('vul_type')
        lang = request.form.get('language')
        regex = request.form.get('regex')
        regex_confirm = request.form.get('regex_confirm')
        description = request.form.get('description')
        rule_id = request.form.get('rule_id')
        repair = request.form.get('repair')
        status = request.form.get('status')
        level = request.form.get('level')

        if not vul_type or vul_type == "":
            return jsonify(tag='danger', msg='vul type error.')
        if not lang or lang == "":
            return jsonify(tag='danger', msg='language error.')
        if not regex or regex == "":
            return jsonify(tag='danger', msg='regex can not be blank')
        if not regex_confirm or regex_confirm == "":
            return jsonify(tag='danger', msg='confirm regex can not be blank')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be blank')
        if not repair or repair == "":
            return jsonify(tag='danger', msg='repair can not be blank')
        if not status or status == "" or (status != '1' and status != '2'):
            return jsonify(tag="danger", msg='status error.')
        if not level or level == "":
            return jsonify(tag='danger', msg='level can not be blank.')

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vul_type
        r.language = lang
        r.regex = regex
        r.regex_confirm = regex_confirm
        r.description = description
        r.repair = repair
        r.status = status
        r.level = level
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        repair = request.form.get('repair')
        if not name or name == "":
            return jsonify(tag='danger', msg='name can not be blank.')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be blank.')
        if not repair or repair == "":
            return jsonify(tag='danger', msg='repair can not be blank.')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        vul = CobraVuls(name, description, repair, current_time, current_time)
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

    if not is_login():
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    vul_id = request.form['vul_id']
    if vul_id:
        v = CobraVuls.query.filter_by(id=vul_id).first()
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        name = request.form.get('name')
        description = request.form.get('description')
        repair = request.form.get('repair')

        if not name or name == "":
            return jsonify(tag='danger', msg='name can not be empty')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be empty')
        if not repair or repair == "":
            return jsonify(tag='danger', msg='repair can not be empty')

        v = CobraVuls.query.filter_by(id=vul_id).first()
        v.name = name
        v.description = description
        v.repair = repair

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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    rules_count = CobraRules.query.count()
    return str(rules_count)


# api: get all vuls count
@web.route(ADMIN_URL + '/all_vuls_count', methods=['GET'])
def all_vuls_count():

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    vuls_count = CobraVuls.query.count()
    return str(vuls_count)


# api: get all projects count
@web.route(ADMIN_URL + '/all_projects_count', methods=['GET'])
def all_projects_count():

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    projects_count = CobraProjects.query.count()
    return str(projects_count)


# api: get all whitelists count
@web.route(ADMIN_URL + '/all_whitelists_count', methods=['GET'])
def all_whitelists_count():

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    whitelists_count = CobraWhiteList.query.count()
    return str(whitelists_count)


# api: get all languages count
@web.route(ADMIN_URL + '/all_languages_count', methods=['GET'])
def all_languages_count():

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    languages_count = CobraLanguages.query.count()
    return str(languages_count)


# show all projects
@web.route(ADMIN_URL + '/projects/<int:page>', methods=['GET'])
def projects(page):

    if not is_login():
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        project_id = request.form.get('id')
        if not project_id or project_id == "":
            return jsonify(tag='danger', msg='project id error.')
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == "POST":
        # get data from request
        project_id = request.form.get('project_id')
        name = request.form.get('name')
        repository = request.form.get('repository')
        author = request.form.get('author')
        remark = request.form.get('remark')

        # check data
        if not project_id or project_id == "":
            return jsonify(tag='danger', msg='wrong project id.')
        if not name or name == "":
            return jsonify(tag='danger', msg='name cannot be empty')
        if not repository or repository == "":
            return jsonify(tag='danger', msg='repository can not be empty')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        project = CobraProjects.query.filter_by(id=project_id).first()
        if not project:
            return jsonify(tag='danger', msg='wrong project id.')

        # update project data
        project.name = name
        project.author = author
        project.remark = remark
        project.repository = repository
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

    if not is_login():
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        project_id = request.form.get('project_id')
        rule_id = request.form.get('rule_id')
        path = request.form.get('path')
        reason = request.form.get('reason')

        if not project_id or project_id == "":
            return jsonify(tag='danger', msg='project id error.')
        if not rule_id or rule_id == "":
            return jsonify(tag='danger', msg='rule id error.')
        if not path or path == "":
            return jsonify(tag='danger', msg='file error.')
        if not reason or reason == "":
            return jsonify(tag='danger', msg='reason error.')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if path[0] != '/':
            path = '/' + path
        whitelist = CobraWhiteList(project_id, rule_id, path, reason, 1, current_time, current_time)
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    whitelist_id = request.form.get('whitelist_id')
    if not whitelist_id or whitelists == "":
        return jsonify(tag='danger', msg='wrong white list id.')

    whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
    try:
        db.session.delete(whitelist)
        db.session.commit()
        return jsonify(tag='success', msg='delete success.')
    except:
        return jsonify(tag='danger', msg='unknown error.')


# edit the special white list
@web.route(ADMIN_URL + '/edit_whitelist/<int:whitelist_id>', methods=['GET', 'POST'])
def edit_whitelist(whitelist_id):

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        whitelist_id = request.form.get('whitelist_id')
        project_id = request.form.get('project')
        rule_id = request.form.get('rule')
        path = request.form.get('path')
        reason = request.form.get('reason')
        status = request.form.get('status')

        if not whitelist_id or whitelist_id == "":
            return jsonify(tag='danger', msg='wrong whitelist')
        if not project_id or project_id == "":
            return jsonify(tag='danger', msg='project can not be empty')
        if not rule_id or rule_id == "":
            return jsonify(tag='danger', msg='rule can not be empty')
        if not path or path == "":
            return jsonify(tag='danger', msg='path can not be empty')
        if not reason or reason == "":
            return jsonify(tag='danger', msg='reason can not be empty')
        if not status or status == "":
            return jsonify(tag='danger', msg='status can not be empty')

        whitelist = CobraWhiteList.query.filter_by(id=whitelist_id).first()
        if not whitelist:
            return jsonify(tag='danger', msg='wrong whitelist')

        whitelist.project_id = project_id
        whitelist.rule_id = rule_id
        whitelist.path = path
        whitelist.reason = reason
        whitelist.status = status

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


# search_rules_bar
@web.route(ADMIN_URL + '/search_rules_bar', methods=['GET'])
def search_rules_bar():

    if not is_login():
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

    if not is_login():
        return redirect(ADMIN_URL + '/index')

    if request.method == 'POST':
        language = request.form.get('language')
        vul = request.form.get('vul')

        rules = None

        if language == 'all' and vul == 'all':
            rules = CobraRules.query.all()
        elif language == 'all' and vul != 'all':
            rules = CobraRules.query.filter_by(vul_id=vul).all()
        elif language != 'all' and vul == 'all':
            rules = CobraRules.query.filter_by(language=language).all()
        elif language != 'all' and vul != 'all':
            rules = CobraRules.query.filter_by(language=language, vul_id=vul).all()
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
    if request.method == "POST":
        language = request.form.get("language")
        extensions = request.form.get("extensions")

        if not language or language == "":
            return jsonify(tag="danger", msg="language name can not be blank.")
        if not extensions or extensions == "":
            return jsonify(tag="danger", msg="extensions can not be blank.")

        l = CobraLanguages(language, extensions)
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
    languages = CobraLanguages.query.all()
    data = {
        'languages': languages,
    }
    return render_template("rulesadmin/languages.html", data=data)


@web.route(ADMIN_URL + "/del_language", methods=['POST'])
def del_language():
    cid = request.form.get("id")
    l = CobraLanguages.query.filter_by(id=cid).first()
    try:
        db.session.delete(l)
        db.session.commit()
        return jsonify(tag="success", msg="delete success.")
    except:
        return jsonify(tag="danger", msg="delete failed.")


@web.route(ADMIN_URL + "/edit_language/<int:language_id>", methods=['POST', 'GET'])
def edit_language(language_id):
    if request.method == "POST":
        language = request.form.get("language")
        extensions = request.form.get("extensions")
        if not language or language == "":
            return jsonify(tag="danger", msg="language name can not be blank.")
        if not extensions or extensions == "":
            return jsonify(tag="danger", msg="extensions can not be blank.")

        l = CobraLanguages.query.filter_by(id=language_id).first()
        try:
            l.language = language
            l.extensions = extensions
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

    if not is_login():
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
            if te == tv['vuls']:
                tv['counts'] += x.counts
                flag = True
                break
        if not flag:
            t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
            t['counts'] = x.counts
        total_vuls.append(t)
    today_vuls = []
    for x in all_vuls_today:
        t = {}
        t['vuls'] = all_cobra_vuls[all_rules[x.rule_id]]
        t['counts'] = x.counts
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
    }
    return render_template("rulesadmin/dashboard.html", data=data)
