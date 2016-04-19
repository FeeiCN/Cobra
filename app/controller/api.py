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
from flask import Flask
from flask.ext.sqlalchemy import SQLAlchemy
import ConfigParser

web = Flask(__name__)


@web.route('/')
def hello_world():
    return 'Hello Cobra!'


@web.route('/add')
def add_task():
    return 'Success'


@web.route('/status')
def status_task():
    return 'pending'


def run():
    config = ConfigParser.ConfigParser()
    config.read('config')
    web.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'mysql')
    db = SQLAlchemy(web)

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
