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
import argparse
from flask import request, Flask, jsonify, render_template, abort
from flask.ext.sqlalchemy import SQLAlchemy
import ConfigParser


class Route:
    template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
    asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/asset')
    print template
    web = Flask(__name__, template_folder=template, static_folder=asset)

    def __init__(self):
        @self.web.route('/', methods=['GET'])
        def homepage():
            return render_template('index.html')

        @self.web.route('/blank')
        def blank():
            return render_template('blank.html')

        @self.web.route('/add', methods=['POST'])
        def add():
            return jsonify(code=1001, msg='success', id=123)

        @self.web.route('/status/<int:id>', methods=['GET'])
        def status(id):
            return jsonify(code=1001, msg='success', status='running')

        @self.web.errorhandler(404)
        def page_not_found(e):
            return render_template('404.html'), 404

    def start(self):
        config = ConfigParser.ConfigParser()
        config.read('config')
        self.web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
        self.web.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'mysql')
        db = SQLAlchemy(self.web)
        host = config.get('cobra', 'host')
        port = config.get('cobra', 'port')
        port = int(port)
        debug = config.get('cobra', 'debug')
        debug = bool(debug)
        self.web.run(host=host, port=port, debug=debug)

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

    def parse_option(self):
        parser = argparse.ArgumentParser(description='Cobra is a open source Code Security Scan System')
        parser.add_argument('string', metavar='project/path', type=str, nargs='+', help='Project Path')
        parser.add_argument('--version', help='Cobra Version')
        args = parser.parse_args()
        print args.string[0]
