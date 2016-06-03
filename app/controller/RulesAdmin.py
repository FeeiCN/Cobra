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

from flask import render_template, request, jsonify

from app import web, CobraRules, CobraVuls, db, CobraLanguages
from app import CobraProjects, CobraWhiteList

# default admin url
ADMIN_URL = '/admin'


@web.route(ADMIN_URL + '/', methods=['GET'])
@web.route(ADMIN_URL + '/index', methods=['GET'])
def index():
    return 'admin/index - todo: login page'


# main view
@web.route(ADMIN_URL + '/main', methods=['GET'])
def main():
    return render_template("rulesadmin/main.html")


# all rules button
@web.route(ADMIN_URL + '/rules', methods=['GET'])
def rules():
    # cobra_rules = CobraRules.query.paginate(1, per_page=5, error_out=False)
    cobra_rules = CobraRules.query.all()
    cobra_vuls = CobraVuls.query.all()
    cobra_lang = CobraLanguages.query.all()
    all_vuls = {}
    all_language = {}
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

    data = {
        # 'paginate': cobra_rules,
        'rules': cobra_rules,
    }

    return render_template('rulesadmin/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/add_new_rule', methods=['GET', 'POST'])
def add_new_rule():
    if request.method == 'POST':
        vul_type = request.form.get('vul_type')
        lang = request.form.get('language')
        regex = request.form.get('regex')
        regex_confirm = request.form.get('regex_confirm')
        description = request.form.get('description')
        repair = request.form.get('repair')

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

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        rule = CobraRules(vul_type, lang, regex, regex_confirm, description, repair,
                          1, current_time, current_time)
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
    if request.method == 'POST':
        vul_type = request.form['vul_type']
        lang = request.form['language']
        regex = request.form['regex']
        description = request.form['description']
        rule_id = request.form['rule_id']

        if not vul_type or vul_type == "":
            return jsonify(tag='danger', msg='vul type error.')
        if not lang or lang == "":
            return jsonify(tag='danger', msg='language error.')
        if not regex or regex == "":
            return jsonify(tag='danger', msg='regex can not be blank')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be blank')

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vul_type
        r.language = lang
        r.regex = regex
        r.description = description
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
            'vul_type': r.vul_id,
            'language': r.language,
            'regex': r.regex,
            'description': r.description,
            'all_vuls': vul_type,
            'all_lang': languages,
        })


# add new vuls button
@web.route(ADMIN_URL + '/add_new_vul', methods=['GET', 'POST'])
def add_new_vul():
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name or name == "":
            return jsonify(tag='danger', msg='name is empty')
        if not description or description == "":
            return jsonify(tag='danger', msg='description is empty')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        vul = CobraVuls(name, description, current_time, current_time)
        try:
            db.session.add(vul)
            db.session.commit()
            return jsonify(tag='success', msg='Add Success.')
        except:
            return jsonify(tag='danger', msg='Add failed. Please try again later.')

    else:
        return render_template('rulesadmin/add_new_vul.html')


# show all vuls click
@web.route(ADMIN_URL + '/vuls', methods=['GET'])
def vuls():
    all_vuls = CobraVuls.query.all()
    data = {
        'vuls': all_vuls
    }
    return render_template('rulesadmin/vuls.html', data=data)


# del special vul
@web.route(ADMIN_URL + '/del_vul', methods=['POST'])
def del_vul():
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
    if request.method == 'POST':
        name = request.form['name']
        description = request.form['description']
        if not name or name == "":
            return jsonify(tag='danger', msg='name can not be empty')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be empty')
        v = CobraVuls.query.filter_by(id=vul_id).first()
        v.name = name
        v.description = description
        try:
            db.session.add(v)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='save failed. Try again later?')
    else:
        v = CobraVuls.query.filter_by(id=vul_id).first()
        return render_template('rulesadmin/edit_vul.html', data={
            'name': v.name,
            'description': v.description,
        })


# api: get all rules count
@web.route(ADMIN_URL + '/all_rules_count', methods=['GET'])
def all_rules_count():
    rules_count = CobraRules.query.count()
    return str(rules_count)


# show all projects
@web.route(ADMIN_URL + '/projects', methods=['GET'])
def projects():
    project = CobraProjects.query.all()
    data = {
        'projects': project,
    }
    return render_template("rulesadmin/projects.html", data=data)


# del the special projects
@web.route(ADMIN_URL + '/del_project', methods=['POST'])
def del_project():
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
@web.route(ADMIN_URL + '/whitelists', methods=['GET'])
def whitelists():
    whitelists = CobraWhiteList.query.all()
    data = {
        'whitelists': whitelists,
    }
    return render_template('rulesadmin/whitelists.html', data=data)


# add new white list
@web.route(ADMIN_URL + '/add_whitelist', methods=['GET', 'POST'])
def add_whitelist():
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
