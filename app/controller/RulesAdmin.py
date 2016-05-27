#!/usr/bin/env python
import time

from flask import render_template, request, jsonify

from app import web, CobraRules, CobraVuls, db

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
    data = {
        # 'paginate': cobra_rules,
        'rules': cobra_rules,
    }

    return render_template('rulesadmin/rules.html', data=data)


# add new rules button
@web.route(ADMIN_URL + '/add_new_rule', methods=['GET', 'POST'])
def add_new_rule():

    if request.method == 'POST':
        return '123'
    else:
        vul_type = CobraVuls.query.all()
        print vul_type
        return render_template('rulesadmin/add_new_rule.html')


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


