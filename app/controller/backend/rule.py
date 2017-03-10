# -*- coding: utf-8 -*-

"""
    backend.rules
    ~~~~~~~~~~~~~

    Implements rules controller

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import datetime

from flask import render_template, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from . import ADMIN_URL
from app import web, db
from app.models import CobraRules, CobraVuls, CobraLanguages, CobraResults, CobraProjects
from utils.validate import ValidateClass, login_required
from engine import static, rule
from utils import config
from pickup import git
from pickup.git import GitError


# all rules button
@web.route(ADMIN_URL + '/rules/', methods=['GET'], defaults={'page': 1, 'keyword': '0', 'author': '0', 'vulnerability_type': 0, 'language': 0})
@web.route(ADMIN_URL + '/rules/<int:page>', methods=['GET'], defaults={'keyword': '0', 'author': '0', 'vulnerability_type': 0, 'language': 0})
@web.route(ADMIN_URL + '/rules/<int:page>/<keyword>', methods=['GET'], defaults={'author': '0', 'vulnerability_type': 0, 'language': 0})
@web.route(ADMIN_URL + '/rules/<int:page>/<keyword>/<author>/<int:vulnerability_type>/<int:language>', methods=['GET'])
@login_required
def rules(page, keyword, author, vulnerability_type, language):
    per_page = 10
    filter_group = (CobraRules.id > 0,)

    if author == '0' and vulnerability_type == 0 and language == 0:
        if keyword == '0':
            # List mode
            filter_group += ()
        else:
            # Only search mode
            filter_group += (CobraRules.description.like("%{}%".format(keyword)),)
    else:
        if keyword != '0':
            filter_group += (CobraRules.description.like("%{}%".format(keyword)),)
        # Filter mode
        if author != '0':
            filter_group += (CobraRules.author == author,)
        if vulnerability_type != 0:
            filter_group += (CobraRules.vul_id == vulnerability_type,)
        if language != 0:
            filter_group += (CobraRules.language == language,)

    rules = CobraRules.query.filter(*filter_group).order_by(CobraRules.id.desc()).limit(per_page).offset((page - 1) * per_page).all()
    total = CobraRules.query.filter(*filter_group).count()

    cobra_vuls = CobraVuls.query.all()
    cobra_lang = CobraLanguages.query.all()
    all_vuls = {}
    all_language = {}
    all_rules = []

    for vul in cobra_vuls:
        all_vuls[vul.id] = vul.name
    for lang in cobra_lang:
        all_language[lang.id] = lang.language
    for index, item in enumerate(rules):
        if item.vul_id in all_vuls:
            vulnerability_type_desc = all_vuls[item.vul_id]
        else:
            vulnerability_type_desc = 'Unknown type'
        if item.language in all_language:
            language_desc = all_language[item.language]
        else:
            language_desc = 'Unknown language'
        all_rules.append({
            'id': item.id,
            'name': item.description,
            'language': language_desc,
            'vulnerability_type': vulnerability_type_desc,
            'updated_at': item.updated_at,
            'status': item.status
        })
    authors = db.session.query(CobraRules.author).group_by(CobraRules.author).all()
    if keyword == '0':
        keyword = ''
    data = {
        'total': total,
        'rules': all_rules,
        'vulnerability_types': cobra_vuls,
        'languages': cobra_lang,
        'authors': authors,
        'page': page,
        'author': author,
        'vulnerability_type': vulnerability_type,
        'language': language,
        'keyword': keyword
    }
    return render_template('backend/rule/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/rules/add/', methods=['GET', 'POST'])
@login_required
def add_new_rule():
    if request.method == 'POST':
        vc = ValidateClass(request, 'vul_type', 'language', 'regex_location', 'repair_block',
                           'description', 'repair', 'verify', 'author', 'level', 'status')
        ret, msg = vc.check_args()
        if not ret:
            return jsonify(code=4004, message=msg)

        current_time = datetime.datetime.now()
        rule = CobraRules(
            vul_id=vc.vars.vul_type,
            language=vc.vars.language,
            regex_location=vc.vars.regex_location,
            regex_repair=request.form.get("regex_repair", ""),
            block_repair=vc.vars.repair_block,
            description=vc.vars.description,
            repair=vc.vars.repair,
            verify=vc.vars.verify,
            author=vc.vars.author,
            status=vc.vars.status,
            level=vc.vars.level,
            created_at=current_time,
            updated_at=current_time
        )
        try:
            db.session.add(rule)
            db.session.commit()
            return jsonify(code=1001, message='add success.')
        except Exception as e:
            return jsonify(code=1004, message='add failed, try again later?' + e.message)
    else:
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        data = {
            'type': 'add',
            'title': 'Create rule',
            'all_vuls': vul_type,
            'all_lang': languages,
            'verify': {},
            'rule': dict()
        }
        return render_template('backend/rule/edit.html', data=data)


# del special rule
@web.route(ADMIN_URL + '/rules/del/', methods=['POST'])
@login_required
def del_rule():
    vc = ValidateClass(request, "id")
    vc.check_args()
    rule_id = vc.vars.id
    if rule_id:

        # 检查该条rule是否存在result和task的依赖
        result = db.session.query(
            CobraResults.task_id
        ).filter(CobraResults.rule_id == rule_id).group_by(CobraResults.task_id).all()
        if len(result):
            # 存在依赖
            task_rely = ""
            for res in result:
                task_rely += str(res.task_id) + ","
            task_rely = task_rely.strip(",")
            message = "Delete failed. Please check and delete the task rely on this rule first.<br />"
            message += "<strong>Rely Tasks: </strong>" + task_rely

            return jsonify(code=1004, message=message)

        r = CobraRules.query.filter_by(id=rule_id).first()
        try:
            db.session.delete(r)
            db.session.commit()
            return jsonify(code=1001, message='delete success.')
        except SQLAlchemyError:
            return jsonify(code=1004, message='delete failed. Try again later?')
    else:
        return jsonify(code=1004, message='wrong id')


# edit special rule
@web.route(ADMIN_URL + '/rules/edit/<int:rule_id>', methods=['GET', 'POST'])
@login_required
def edit_rule(rule_id):
    if request.method == 'POST':

        vc = ValidateClass(request, "vul_type", "language", "regex_location", "repair_block", "description",
                           "rule_id", "repair", 'verify', "author", "status", "level")
        ret, msg = vc.check_args()

        regex_repair = request.form.get("regex_repair", "")

        if not ret:
            return jsonify(code=4004, message=msg)

        r = CobraRules.query.filter_by(id=rule_id).first()
        r.vul_id = vc.vars.vul_type
        r.language = vc.vars.language
        r.block_repair = vc.vars.repair_block
        r.regex_location = vc.vars.regex_location
        r.regex_repair = regex_repair
        r.description = vc.vars.description
        r.repair = vc.vars.repair
        r.verify = vc.vars.verify
        r.author = vc.vars.author
        r.status = vc.vars.status
        r.level = vc.vars.level
        r.updated_at = datetime.datetime.now()
        try:
            db.session.add(r)
            db.session.commit()
            return jsonify(code=1001, message='success')
        except SQLAlchemyError:
            return jsonify(code=4004, message='save failed. Try again later?')
    else:
        r = CobraRules.query.filter_by(id=rule_id).first()
        verify_data = rule.Rule(r.regex_location, r.regex_repair, r.verify).verify()
        vul_type = CobraVuls.query.all()
        languages = CobraLanguages.query.all()
        projects = CobraProjects.query.with_entities(CobraProjects.id, CobraProjects.name, CobraProjects.repository).all()
        return render_template('backend/rule/edit.html', data={
            'type': 'edit',
            'title': 'Edit rule',
            'id': r.id,
            'rule': r,
            'verify': verify_data,
            'all_vuls': vul_type,
            'all_lang': languages,
            'projects': projects
        })


@web.route(ADMIN_URL + '/rules/test/', methods=['POST'])
@login_required
def test_rule():
    vc = ValidateClass(request, 'rid', 'pid')
    ret, msg = vc.check_args()
    if not ret:
        return jsonify(code=4004, message=msg)

    # all projects
    if int(vc.vars.pid) == 0:
        project_directory = os.path.join(config.Config('upload', 'directory').value, 'versions')
    else:
        project = CobraProjects.query.filter(CobraProjects.id == vc.vars.pid).first()
        if 'gitlab' in project.repository or 'github' in project.repository:
            username = config.Config('git', 'username').value
            password = config.Config('git', 'password').value
            gg = git.Git(project.repository, branch='master', username=username, password=password)
            try:
                clone_ret, clone_err = gg.clone()
                if clone_ret is False:
                    return jsonify(code=4001, message='Clone Failed ({0})'.format(clone_err))
            except GitError:
                return jsonify(code=4001, message='Exception')
            project_directory = gg.repo_directory
        else:
            project_directory = project.repository
    data = static.Static(project_directory, project_id=vc.vars.pid, rule_id=vc.vars.rid).analyse(test=True)
    data = '\r\n'.join(data)
    return jsonify(code=1001, message=data)
