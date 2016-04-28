#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import os
from flask import request, Flask, jsonify, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
import ConfigParser


class Api:
    template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    print template
    web = Flask(__name__, template_folder=template)

    def __init__(self):
        @self.web.route('/')
        def hello_world():
            return 'Hello Cobra!'

        @self.web.route('/add')
        def add_task():
            if request.method == "POST":
                return jsonify(code=1001, msg='success', id=123)
            else:
                abort(404)

        @self.web.route('/status')
        def status_task():
            return jsonify(code=1001, msg='success', status='running')

        @self.web.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

    def run(self):
        config = ConfigParser.ConfigParser()
        config.read('config')
        self.web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.web.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'mysql')
        db = SQLAlchemy(self.web)
        self.web.run()

        #
        # Whitelist Table
        #
        class Whitelist(db.Model):
            id = db.Column(db.Integer, primary_key=True)
            url = db.Column(db.String(256))
            remark = db.Column(db.String(56))
            status = db.Column(db.Integer)
            created = db.Column(db.Integer)
            updated = db.Column(db.Integer)

            def __repr__(self):
                return self.url

        #
        # Result Table
        #
        class Result(db.Model):
            id = db.Column(db.Integer, primary_key=True)

        #
        # Log Table
        #
        class Log(db.Model):
            id = db.Column(db.Integer, primary_key=True)
