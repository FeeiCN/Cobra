#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    app.__init__
    ~~~~~~~~~~~~

    Implements app

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import sys
import subprocess
import logging

from flask import Flask
from flask_script import Manager, Server, Option, Command
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap
from sqlalchemy import exc

from utils import config, common

logging = logging.getLogger(__name__)

reload(sys)
sys.setdefaultencoding('utf-8')

# 应用配置
template = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates')
asset = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'templates/asset')
web = Flask(__name__, template_folder=template, static_folder=asset)
web.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True
web.config['SQLALCHEMY_DATABASE_URI'] = config.Config('database', 'mysql').value
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

# just use the migration script's app context when you import the models
# http://stackoverflow.com/questions/33905706/flask-migrate-seemed-to-delete-all-my-database-data
with web.app_context():
    from models import *

manager = Manager(web)

host = config.Config('cobra', 'host').value
port = config.Config('cobra', 'port').value
port = int(port)


class Statistic(Command):
    """
    统计代码相关信息(代码行数/注释行数/空白行数)
    """
    option_list = (
        Option('--target', '-t', dest='target', help='directory'),
        Option('--tid', '-i', dest='tid', help='scan task id')
    )

    def run(self, target=None, tid=None):
        if target is None:
            logging.critical("Please set --target param")
            sys.exit()
        if tid is None:
            logging.critical("Please set --tid param")
            sys.exit()

        # Statistic Code
        p = subprocess.Popen(['cloc', target], stdout=subprocess.PIPE)
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
                        logging.info("Statistic code number done")
                    except Exception as e:
                        logging.error("Statistic code number failed" + str(e.message))


class Scan(Command):
    """
    扫描漏洞
    """
    option_list = (
        Option('--target', '-t', dest='target', help='scan target(directory/git repository/svn url/file path)'),
        Option('--tid', '-i', dest='tid', help='scan task id'),
        Option('--pid', '-p', dest='pid', help='scan project id'),
    )

    def run(self, target=None, tid=None, pid=None):
        if target is None:
            logging.critical("Please set --target param")
            sys.exit()
        if tid is not None:
            task_id = tid
            # Start Time For Task
            t = CobraTaskInfo.query.filter_by(id=tid).first()
            if t is None:
                logging.critical("Task id doesn't exists.")
                sys.exit()
            if t.status not in [0, 1]:
                logging.critical("Task Already Scan.")
                sys.exit()
            t.status = 1
            t.time_start = int(time.time())
            t.updated_at = time.strftime('%Y-%m-%d %X', time.localtime())
            try:
                db.session.add(t)
                db.session.commit()
            except Exception as e:
                logging.error("Set start time failed" + str(e.message))
        else:
            task_id = None

        if os.path.isdir(target) is not True:
            logging.critical('Target is not directory')
            sys.exit()
        from engine import static
        static.Static(target, task_id=task_id, project_id=pid).analyse()


class Install(Command):
    """
    初始化表结构
    """

    def run(self):
        # create database structure
        logging.debug("Start create database structure...")
        try:
            db.create_all()
        except exc.SQLAlchemyError as e:
            logging.critical("MySQL database error: {0}\nFAQ: {1}".format(e, 'https://github.com/wufeifei/cobra/wiki/Error#mysql'))
            sys.exit(0)
        logging.debug("Create Structure Success.")
        # insert base data
        from app.models import CobraAuth, CobraLanguages, CobraAdminUser, CobraVuls
        # table `auth`
        logging.debug('Insert api key...')
        auth = CobraAuth('manual', common.md5('CobraAuthKey'), 1)
        db.session.add(auth)

        # table `languages`
        logging.debug('Insert language...')
        languages = {
            "php": ".php|.php3|.php4|.php5",
            "jsp": ".jsp",
            "java": ".java",
            "html": ".html|.htm|.phps|.phtml",
            "js": ".js",
            "backup": ".zip|.bak|.tar|.tar.gz|.rar",
            "xml": ".xml",
            "image": ".jpg|.png|.bmp|.gif|.ico|.cur",
            "font": ".eot|.otf|.svg|.ttf|.woff",
            "css": ".css|.less|.scss|.styl",
            "exe": ".exe",
            "shell": ".sh",
            "log": ".log",
            "text": ".txt|.text",
            "flash": ".swf",
            "yml": ".yml",
            "cert": ".p12|.crt|.key|.pfx|.csr",
            "psd": ".psd",
            "iml": ".iml",
            "spf": ".spf",
            "markdown": ".md",
            "office": ".doc|.docx|.wps|.rtf|.csv|.xls|.ppt",
            "bat": ".bat",
            "PSD": ".psd",
            "Thumb": ".db",
        }
        for language, extensions in languages.items():
            a_language = CobraLanguages(language, extensions)
            db.session.add(a_language)

        # table `user`
        logging.debug('Insert admin user...')
        username = 'admin'
        password = 'admin123456!@#'
        role = 1  # 1: super admin, 2: admin, 3: rules admin
        a_user = CobraAdminUser(username, password, role)
        db.session.add(a_user)

        # table `vuls`
        logging.debug('Insert vuls...')
        vuls = [
            'SQL Injection',
            'LFI/RFI',
            'Header Injection',
            'XSS',
            'CSRF',
            'Logic Bug',
            'Command Execute',
            'Code Execute',
            'Information Disclosure',
            'Data Exposure',
            'Xpath Injection',
            'LDAP Injection',
            'XML/XXE Injection',
            'Unserialize',
            'Variables Override',
            'URL Redirect',
            'Weak Function',
            'Buffer Overflow',
            'Deprecated Function',
            'Stack Trace',
            'Resource Executable',
            'SSRF',
            'Misconfiguration',
            'Components'
        ]
        for vul in vuls:
            a_vul = CobraVuls(vul, 'Vul Description', 'Vul Repair', 0)
            db.session.add(a_vul)

        # commit
        db.session.commit()
        logging.debug('All Done.')


class Repair(Command):
    """
    检测已有漏洞修复状况
    Usage: python cobra.py repair --pid=your_project_id
    """
    option_list = (
        Option('--pid', '-p', dest='pid', help='scan project id'),
    )

    def run(self, pid=None):
        from app.models import CobraResults, CobraRules, CobraVuls
        from engine.core import Core
        from pickup.git import Git
        if pid is None:
            logging.critical("Please set --pid param")
            sys.exit()
        # 项目信息
        project_info = CobraProjects.query.filter_by(id=pid).first()
        if project_info.repository[0] == '/':
            project_directory = project_info.repository
        else:
            project_directory = Git(project_info.repository).repo_directory
        # 漏洞第三方ID
        vuln_all = CobraVuls.query.all()
        vuln_all_d = {}
        for vuln in vuln_all:
            vuln_all_d[vuln.id] = vuln.third_v_id
        # 未修复的漏洞数据
        result_all = db.session().query(CobraRules, CobraResults).join(CobraResults, CobraResults.rule_id == CobraRules.id).filter(
            CobraResults.project_id == pid,
            CobraResults.status < 2
        ).all()
        for index, (rule, result) in enumerate(result_all):
            # 核心规则校验
            result_info = {
                'task_id': result.task_id,
                'project_id': result.project_id,
                'project_directory': project_directory,
                'rule_id': result.rule_id,
                'file_path': result.file,
                'line_number': result.line,
                'code_content': result.code,
                'third_party_vulnerabilities_name': rule.description,
                'third_party_vulnerabilities_type': vuln_all_d[rule.vul_id]
            }
            ret_status, ret_result = Core(result_info, rule, project_info.name, []).repair()
            if ret_status is False:
                logging.info("修复 R: False {0}".format(ret_result))
                continue


# 命令行
manager.add_command('start', Server(host=host, port=port))
manager.add_command('scan', Scan())
manager.add_command('statistic', Statistic())
manager.add_command('install', Install())
manager.add_command('repair', Repair())

# 前端路由
from app.controller import route
from app.controller import api

# 后端服务
from app.controller.backend import BackendAPIController
from app.controller.backend import DashboardController
from app.controller.backend import IndexController
from app.controller.backend import LanguagesController
from app.controller.backend import ProjectsController
from app.controller.backend import RulesController
from app.controller.backend import SearchController
from app.controller.backend import TasksController
from app.controller.backend import VulsController
from app.controller.backend import WhiteListsController
from app.controller.backend import FramesController
