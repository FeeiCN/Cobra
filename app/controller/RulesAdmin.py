#!/usr/bin/env python

from flask import render_template

from app import web, CobraRules

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
@web.route(ADMIN_URL + '/add_new', methods=['GET'])
def add_new():
    return 'admin/add_new'


# api: get all rules count
@web.route(ADMIN_URL + '/all_rules_count', methods=['GET'])
def all_rules_count():
    rules_count = CobraRules.query.count()
    return str(rules_count)

