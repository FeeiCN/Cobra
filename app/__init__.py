#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.__init__
    ~~~~~~~~~~~~

    Implements app

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import sys
from flask import Flask
from flask_bootstrap import Bootstrap
from flask_script import Manager, Server
from flask_sqlalchemy import SQLAlchemy
from flask_cache import Cache

from utils import config

VERSION = '1.7'

reload(sys)
sys.setdefaultencoding('utf-8')

# Application Configuration
template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/asset')
web = Flask(__name__, template_folder=template, static_folder=asset)
web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
web.config['SQLALCHEMY_DATABASE_URI'] = config.Config('database', 'mysql').value
# web.config['SQLALCHEMY_ECHO'] = True
web.secret_key = config.Config('cobra', 'secret_key').value

bootstrap = Bootstrap(web)

# set bootstrap css and jquery js to local
web.config['BOOTSTRAP_SERVE_LOCAL'] = True

# upload directory
upload_directory = os.path.join(config.Config('upload', 'directory').value, 'uploads')
if os.path.isdir(upload_directory) is not True:
    os.makedirs(upload_directory)
web.config['UPLOAD_FOLDER'] = upload_directory
web.config['MAX_CONTENT_LENGTH'] = int(config.Config('upload', 'max_size').value) * 1024 * 1024

db = SQLAlchemy(web)

# Flask-Cache
cache = Cache(web, config={'CACHE_TYPE': 'simple'})

#
# # just use the migration script's app context when you import the models
# # http://stackoverflow.com/questions/33905706/flask-migrate-seemed-to-delete-all-my-database-data
# with web.app_context():
#     from models import *

description = "Cobra v{0} ( https://github.com/wufeifei/cobra ) is a static code analysis system that automates the detecting vulnerabilities and security issue.".format(VERSION)

manager = Manager(web, description=description)

host = config.Config('cobra', 'host').value
port = config.Config('cobra', 'port').value
port = int(port)

# CLI
from app.cli import report, repair, install, scan, statistic, pull

manager.add_command('start', Server(host=host, port=port, threaded=True))
manager.add_command('scan', scan.Scan())
manager.add_command('statistic', statistic.Statistic())
manager.add_command('install', install.Install())
manager.add_command('repair', repair.Repair())
manager.add_command('report', report.Report())
manager.add_command('pull', pull.Pull())

# Front route
from app.controller.front import route, api

# Background route
from app.controller.backend import api, dashboard, index, language, project, rule, task, vulnerability, whitelist, framework, report, result
