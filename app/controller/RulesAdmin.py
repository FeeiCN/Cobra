#!/usr/bin/env python
import time

from flask import render_template, request, jsonify

from app import web, CobraRules, CobraVuls, db, CobraSupportLanguage
from app import CobraProject

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
    cobra_lang = CobraSupportLanguage.query.all()
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
        vul_type = request.form['vul_type']
        lang = request.form['language']
        regex = request.form['regex']
        description = request.form['description']

        if not vul_type or vul_type == "":
            return jsonify(tag='danger', msg='vul type error.')
        if not lang or lang == "":
            return jsonify(tag='danger', msg='language error.')
        if not regex or regex == "":
            return jsonify(tag='danger', msg='regex can not be blank')
        if not description or description == "":
            return jsonify(tag='danger', msg='description can not be blank')

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        rule = CobraRules(vul_type, lang, regex, description, current_time, current_time)
        try:
            db.session.add(rule)
            db.session.commit()
            return jsonify(tag='success', msg='add success.')
        except:
            return jsonify(tag='danger', msg='add failed, try again later?')
    else:
        vul_type = CobraVuls.query.all()
        languages = CobraSupportLanguage.query.all()
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
        languages = CobraSupportLanguage.query.all()
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
    project = CobraProject.query.all()
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
        project = CobraProject.query.filter_by(id=project_id).first()
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
        repo_type = request.form.get('repo_type')
        repository = request.form.get('repository')
        branch = request.form.get('branch')
        username = request.form.get('username')
        password = request.form.get('password')

        # check data
        if not project_id or project_id == "":
            return jsonify(tag='danger', msg='wrong project id.')
        if not name or name == "":
            return jsonify(tag='danger', msg='name cannot be empty')
        if not repo_type or repo_type == "":
            return jsonify(tag='danger', msg='repo type cannot be empty')
        if not repository or repository == "":
            return jsonify(tag='danger', msg='repository can not be empty')
        if not branch or branch == "":
            return jsonify(tag='danger', msg="branch can not be empty")

        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        repo_type = 1 if repo_type == "git" else 2
        project = CobraProject.query.filter_by(id=project_id).first()
        if not project:
            return jsonify(tag='danger', msg='wrong project id.')

        # update project data
        project.name = name
        project.repo_type = 1 if repo_type == 'git' else 2
        project.repository = repository
        project.branch = branch
        project.username = username if username and username != "" else None
        project.password = password if password and password != "" else None
        project.updated_at = current_time
        try:
            db.session.add(project)
            db.session.commit()
            return jsonify(tag='success', msg='save success.')
        except:
            return jsonify(tag='danger', msg='Unknown error.')
    else:
        project = CobraProject.query.filter_by(id=project_id).first()
        return render_template('rulesadmin/edit_project.html', data={
            'project': project
        })




