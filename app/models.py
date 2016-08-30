# -*- coding: utf-8 -*-

"""
    app.models
    ~~~~~~~~~~

    Implements models

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""

import time
from sqlalchemy.schema import UniqueConstraint, Index
from sqlalchemy.dialects.mysql import TINYINT, INTEGER, SMALLINT
from werkzeug.security import check_password_hash, generate_password_hash
from app import db


class CobraTaskInfo(db.Model):
    """
    Tasks for project
    """
    __tablename__ = 'tasks'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    target = db.Column(db.String(255), nullable=False, default=None)
    branch = db.Column(db.String(64), nullable=False, default=None)
    scan_way = db.Column(SMALLINT(6), nullable=False, default=None)
    new_version = db.Column(db.String(40), nullable=False, default=None)
    old_version = db.Column(db.String(40), nullable=False, default=None)
    time_consume = db.Column(db.Integer, nullable=False, default=None)
    time_start = db.Column(db.Integer, nullable=False, default=None)
    time_end = db.Column(db.Integer, nullable=False, default=None)
    file_count = db.Column(db.Integer, nullable=False, default=None)
    code_number = db.Column(db.Integer, nullable=False, default=None)
    status = db.Column(TINYINT(4), nullable=False, default=0, index=True)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    def __init__(self, target, branch, scan_way, new_version, old_version, time_consume, time_start, time_end, file_count, code_number, status, created_at=None, updated_at=None):
        self.target = target
        self.branch = branch
        self.scan_way = scan_way
        self.new_version = new_version
        self.old_version = old_version
        self.time_consume = time_consume
        self.time_start = time_start
        self.time_end = time_end
        self.file_count = file_count
        self.code_number = code_number
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return '<task_info %r - %r>' % (self.id, self.target)


class CobraRules(db.Model):
    """
    Rules for vulnerabilities and languages
    """
    __tablename__ = 'rules'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    vul_id = db.Column(TINYINT, nullable=True, default=None, index=True)
    language = db.Column(TINYINT, nullable=True, default=None, index=True)
    regex_location = db.Column(db.String(512), nullable=False, default=None)
    regex_repair = db.Column(db.String(512), nullable=False, default=None)
    block_repair = db.Column(TINYINT(2), nullable=False, default=None)
    description = db.Column(db.String(256), nullable=False, default=None)
    repair = db.Column(db.String(512), nullable=False, default=None)
    status = db.Column(TINYINT(2), nullable=False, default=None)
    level = db.Column(TINYINT(2), nullable=False, default=None)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    def __init__(self, vul_id, language, regex_location, regex_repair, block_repair, description, repair, status, level, created_at=None, updated_at=None):
        self.vul_id = vul_id
        self.language = language
        self.regex_location = regex_location
        self.regex_repair = regex_repair
        self.block_repair = block_repair
        self.description = description
        self.repair = repair
        self.status = status
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraRules %r - %r: %r>" % (self.id, self.language, self.regex)


class CobraVuls(db.Model):
    """
    Vulnerabilities types
    """
    __tablename__ = 'vuls'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(56), nullable=False, default=None)
    description = db.Column(db.String(512), nullable=False, default=None)
    repair = db.Column(db.String(512), nullable=False, default=None)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    def __init__(self, name, description, repair, created_at=None, updated_at=None):
        self.name = name
        self.description = description
        self.repair = repair
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraVuls %r - %r>" % (self.id, self.name)


class CobraLanguages(db.Model):
    """
    Languages for files
    """
    __tablename__ = 'languages'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    language = db.Column(db.String(11), nullable=False, index=True)
    extensions = db.Column(db.String(128), nullable=False, default=None)

    def __init__(self, language, extensions):
        self.language = language
        self.extensions = extensions

    def __repr__(self):
        return "<CobraLanguage %r - %r>" % (self.id, self.language)


class CobraResults(db.Model):
    """
    Results for task
    """
    __tablename__ = 'results'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    task_id = db.Column(INTEGER(11), nullable=False, default=None)
    rule_id = db.Column(INTEGER(11), nullable=False, default=None)
    file = db.Column(db.String(512), nullable=False, default=None)
    line = db.Column(INTEGER(11), nullable=False, default=None)
    code = db.Column(db.String(512), nullable=False, default=None)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    __table_args__ = (Index('ix_task_id_rule_id', task_id, rule_id), {"mysql_charset": "utf8mb4"})

    def __init__(self, task_id, rule_id, file_path, line, code, created_at=None, updated_at=None):
        self.task_id = task_id
        self.rule_id = rule_id
        self.file = file_path
        self.line = line
        self.code = code
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraResults %r - %r>" % (self.id, self.task_id)


class CobraProjects(db.Model):
    """
    Projects for all
    """
    __tablename__ = 'projects'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    repository = db.Column(db.String(512), nullable=False, default=None)
    url = db.Column(db.String(512), nullable=False, default=None)
    name = db.Column(db.String(50), nullable=False, default=None)
    author = db.Column(db.String(50), nullable=False, default=None)
    framework = db.Column(db.String(32), nullable=False, default=None)
    pe = db.Column(db.String(32), nullable=False, default=None)
    remark = db.Column(db.String(512), nullable=False, default=None)
    last_scan = db.Column(db.DateTime, nullable=False, default=None)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    def __init__(self, repository, url, name, author, framework, pe, remark, last_scan, created_at=None, updated_at=None):
        self.repository = repository
        self.url = url
        self.name = name
        self.author = author
        self.framework = framework
        self.pe = pe
        self.remark = remark
        self.last_scan = last_scan
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraProjects %r - %r>" % (self.id, self.name)


class CobraWhiteList(db.Model):
    """
    Whitelist for project and rule
    """
    __tablename__ = 'whitelist'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    project_id = db.Column(db.Integer, default=None, nullable=False)
    rule_id = db.Column(db.Integer, default=None, nullable=False)
    path = db.Column(db.String(512), default=None, nullable=False)
    reason = db.Column(db.String(512), default=None, nullable=False)
    status = db.Column(TINYINT, default=None, nullable=False)
    created_at = db.Column(db.DateTime, default=None, nullable=False)
    updated_at = db.Column(db.DateTime, default=None, nullable=False)

    __table_args__ = (Index('ix_project_id_rule_id', project_id, rule_id), {"mysql_charset": "utf8mb4"})

    def __init__(self, project_id, rule_id, path, reason, status, created_at=None, updated_at=None):
        self.project_id = project_id
        self.rule_id = rule_id
        self.path = path
        self.reason = reason
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraWhiteList %r-%r:%r>" % (self.project_id, self.rule_id, self.reason)


class CobraAuth(db.Model):
    """
    API for third-party transfer
    """
    __tablename__ = 'auth'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(52), default=None, nullable=False, unique=True)
    key = db.Column(db.String(256), default=None, nullable=False)
    status = db.Column(TINYINT, default=0, nullable=False)
    created_at = db.Column(db.DateTime, default=None, nullable=False)
    updated_at = db.Column(db.DateTime, default=None, nullable=False)

    def __init__(self, name, key, status, created_at=None, updated_at=None):
        self.name = name
        self.key = key
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraAuth %r-%r>" % (self.name, self.key)


class CobraExt(db.Model):
    """
    Statistic task extension distributing
    """
    __tablename__ = 'ext'
    __table_args__ = (UniqueConstraint('task_id', 'ext'), {"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER, primary_key=True, autoincrement=True, nullable=False)
    task_id = db.Column(db.Integer, default=None, nullable=True, index=True)
    ext = db.Column(db.String(32), default=None, nullable=True)
    amount = db.Column(db.Integer, default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=None, nullable=True)
    updated_at = db.Column(db.DateTime, default=None, nullable=True)

    def __init__(self, task_id, ext, amount, created_at=None, updated_at=None):
        self.task_id = task_id
        self.ext = ext
        self.amount = amount
        self.created_at = created_at
        self.updated_at = updated_at
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraExt %r-%r>" % (self.ext, self.amount)


class CobraAdminUser(db.Model):
    """
    User for login
    :role: 1-super admin, 2-admin, 3-rule admin
    """
    __tablename__ = 'user'
    __table_args__ = ({"mysql_charset": "utf8mb4"})

    id = db.Column(INTEGER, primary_key=True, autoincrement=True, nullable=None)
    username = db.Column(db.String(64), nullable=False, default=None, unique=True)
    password = db.Column(db.String(256), nullable=False, default=None)
    role = db.Column(TINYINT(2), nullable=False, default=None)
    last_login_time = db.Column(db.DateTime, nullable=False, default=None)
    last_login_ip = db.Column(db.String(16), nullable=False, default=None)
    created_at = db.Column(db.DateTime, nullable=False, default=None)
    updated_at = db.Column(db.DateTime, nullable=False, default=None)

    def __init__(self, username, password, role, last_login_time=None, last_login_ip=None, created_at=None, updated_at=None):
        self.username = username
        self.generate_password(password)
        self.role = role
        self.last_login_time = last_login_time
        self.last_login_ip = last_login_ip
        self.created_at = created_at
        self.updated_at = updated_at
        if last_login_ip is None:
            self.last_login_ip = ''
        current_time = time.strftime('%Y-%m-%d %X', time.localtime())
        if last_login_time is None:
            self.last_login_time = current_time
        else:
            self.last_login_time = last_login_time
        if created_at is None:
            self.created_at = current_time
        else:
            self.created_at = created_at
        if updated_at is None:
            self.updated_at = current_time
        else:
            self.updated_at = updated_at

    def __repr__(self):
        return "<CobraAdminUser %r-%r>" % (self.username, self.role)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_password(self, password):
        self.password = generate_password_hash(password)
