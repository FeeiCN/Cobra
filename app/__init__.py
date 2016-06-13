#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import ConfigParser
import os
import sys
import time
import subprocess

from flask import Flask
from flask_migrate import MigrateCommand, Migrate
from flask_script import Manager, Server, Option, Command
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

from utils import log

reload(sys)
sys.setdefaultencoding('utf-8')

template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/asset')
web = Flask(__name__, template_folder=template, static_folder=asset)

config = ConfigParser.ConfigParser()
config.read('config')
web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
web.config['SQLALCHEMY_DATABASE_URI'] = config.get('database', 'mysql')
web.secret_key = config.get('cobra', 'secret_key')

bootstrap = Bootstrap(web)

db = SQLAlchemy(web)

# just use the migration script's app context when you import the models
# http://stackoverflow.com/questions/33905706/flask-migrate-seemed-to-delete-all-my-database-data
with web.app_context():
    from models import *

migrate = Migrate(web, db)
manager = Manager(web)


class Statistic(Command):
    option_list = (
        Option('--target', '-t', dest='target', help='directory'),
        Option('--tid', '-i', dest='tid', help='scan task id')
    )

    def run(self, target=None, tid=None):
        if target is None:
            log.critical("Please set --target param")
            sys.exit()
        if tid is None:
            log.critical("Please set --tid param")
            sys.exit()

        # Statistic Code
        p = subprocess.Popen(
            ['cloc', target], stdout=subprocess.PIPE)
        (output, err) = p.communicate()
        rs = output.split("\n")
        for r in rs:
            r_e = r.split()
            if len(r_e) > 3 and r_e[0] == 'SUM:':
                t = CobraTaskInfo.query.filter_by(id=tid).first()
                if t is not None:
                    t.code_number = r_e[4]
                    try:
                        db.session.add(t)
                        db.session.commit()
                        log.info("Statistic code number done")
                    except Exception as e:
                        log.error("Statistic code number failed" + str(e.message))


class Scan(Command):
    option_list = (
        Option('--target', '-t', dest='target', help='scan target(directory/git repository/svn url/file path)'),
        Option('--tid', '-i', dest='tid', help='scan task id'),
        Option('--pid', '-p', dest='pid', help='scan project id'),
    )

    def parse_target(self, target=None):
        if target[len(target) - 4:] == '.git':
            return 'git'
        elif os.path.isdir(target) is True:
            return 'directory'
        elif os.path.isfile(target) is True:
            filename, file_extension = os.path.splitext(target)
            if file_extension in ['.tar.gz', '.rar', '.zip']:
                return 'compress'
            else:
                return 'file'
        elif target[0:7] == 'http://' or target[0:8] == 'https://':
            return 'svn'
        else:
            return False

    def run(self, target=None, tid=None, pid=None):
        if target is None:
            log.critical("Please set --target param")
            sys.exit()
        if tid is not None:
            task_id = tid
            # Start Time For Task
            t = CobraTaskInfo.query.filter_by(id=tid).first()
            if t is None:
                log.critical("Task id doesn't exists.")
                sys.exit()
            if t.status not in [0, 1]:
                log.critical("Task Already Scan.")
                sys.exit()
            t.status = 1
            t.time_start = int(time.time())
            t.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
            try:
                db.session.add(t)
                db.session.commit()
            except Exception as e:
                log.error("Set start time failed" + str(e.message))
        else:
            task_id = None

        target_type = self.parse_target(target)
        if target_type is False:
            log.error("""
                Git Repository: must .git end
                SVN Repository: can http:// or https://
                Directory: must be local directory
                File: must be single file or tar.gz/zip/rar compress file
                """)
        from engine import static
        s = static.Static(target, task_id=task_id, project_id=pid)
        if target_type is 'directory':
            s.analyse()
        elif target_type is 'compress':
            from utils.decompress import Decompress
            # load an compressed file. only tar.gz, rar, zip supported.
            dc = Decompress(target)
            # decompress it. And there will create a directory named "222_test.tar".
            dc.decompress()
            s.analyse()
        elif target_type is 'file':
            s.analyse()
        elif target_type is 'git':
            from pickup.GitTools import Git
            g = Git(target, branch='master')
            g.get_repo()
            if g.clone() is True:
                s.analyse()
            else:
                log.critical("Git clone failed")
        elif target_type is 'svn':
            log.warning("Not Support SVN Repository")


host = config.get('cobra', 'host')
port = config.get('cobra', 'port')
port = int(port)

manager.add_command('db', MigrateCommand)
manager.add_command('start', Server(host=host, port=port))
manager.add_command('scan', Scan())
manager.add_command('statistic', Statistic())

from app.controller import route
from app.controller import RulesAdmin
from app.controller import api

log.info('Cobra Engine Started')
