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
import sqlalchemy
import ConfigParser

app = Flask(__name__)


@app.route('/')
def hello_world():
    return 'Hello Cobra!'


@app.route('/add')
def add_task():
    return 'Success'


@app.route('/status')
def status_task():
    return 'pending'


def run():
    app.run()
