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
@web.route(ADMIN_URL + '/add_new_rule', methods=['GET'])
def add_new_rule():
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


# api: get all rules count
@web.route(ADMIN_URL + '/all_rules_count', methods=['GET'])
def all_rules_count():
    rules_count = CobraRules.query.count()
    return str(rules_count)

