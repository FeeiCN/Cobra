#!/usr/bin/env python

from flask import render_template

from app import web

# default admin url
admin_url = '/admin'


@web.route(admin_url+'/', methods=['GET'])
@web.route(admin_url+'/index', methods=['GET'])
def index():
    return 'admin/index'


@web.route(admin_url+'/rules', methods=['GET'])
def rules():
    return render_template('rulesadmin/index.html')

