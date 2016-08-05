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

import time
from sqlalchemy.dialects.mysql import TINYINT, INTEGER, SMALLINT
from werkzeug.security import check_password_hash, generate_password_hash
from app import db


# task_info table. store task information.
class CobraTaskInfo(db.Model):
    __tablename__ = 'tasks'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    target = db.Column(db.String(255), nullable=True, default=None)
    branch = db.Column(db.String(64), nullable=True, default=None)
    scan_way = db.Column(SMALLINT(6), nullable=True, default=None)
    new_version = db.Column(db.String(40), nullable=True, default=None)
    old_version = db.Column(db.String(40), nullable=True, default=None)
    time_consume = db.Column(db.Integer, nullable=True, default=None)
    time_start = db.Column(db.Integer, nullable=True, default=None)
    time_end = db.Column(db.Integer, nullable=True, default=None)
    file_count = db.Column(db.Integer, nullable=True, default=None)
    code_number = db.Column(db.Integer, nullable=True, default=None)
    status = db.Column(TINYINT(4), nullable=True, default=0)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, target, branch, scan_way, new_version, old_version, time_consume, time_start, time_end,
                 file_count, code_number, status, created_at, updated_at):
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

    def __repr__(self):
        return '<task_info %r - %r>' % (self.id, self.target)


class CobraRules(db.Model):
    __tablename__ = 'rules'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    vul_id = db.Column(TINYINT(unsigned=False), nullable=True, default=None)
    language = db.Column(TINYINT(unsigned=False), nullable=True, default=None)
    regex = db.Column(db.String(512), nullable=True, default=None)
    regex_confirm = db.Column(db.String(512), nullable=True, default=None)
    description = db.Column(db.String(256), nullable=True, default=None)
    repair = db.Column(db.String(512), nullable=True, default=None)
    status = db.Column(TINYINT(2), nullable=True, default=None)
    level = db.Column(TINYINT(2), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, vul_id, language, regex, regex_confirm, description, repair, status, level, created_at,
                 updated_at):
        self.vul_id = vul_id
        self.language = language
        self.regex = regex
        self.regex_confirm = regex_confirm
        self.description = description
        self.repair = repair
        self.status = status
        self.level = level
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraRules %r - %r: %r>" % (self.id, self.language, self.regex)


class CobraVuls(db.Model):
    __tablename__ = 'vuls'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(56), nullable=True, default=None)
    description = db.Column(db.String(512), nullable=True, default=None)
    repair = db.Column(db.String(512), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, name, description, repair, created_at, updated_at):
        self.name = name
        self.description = description
        self.repair = repair
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraVuls %r - %r>" % (self.id, self.name)


class CobraLanguages(db.Model):
    __tablename__ = 'languages'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    language = db.Column(db.String(11), nullable=False)
    extensions = db.Column(db.String(128), nullable=True, default=None)

    def __init__(self, language, extensions):
        self.language = language
        self.extensions = extensions

    def __repr__(self):
        return "<CobraLanguage %r - %r>" % (self.id, self.language)


class CobraResults(db.Model):
    __tablename__ = 'results'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    task_id = db.Column(INTEGER(11), nullable=True, default=None)
    rule_id = db.Column(INTEGER(11), nullable=True, default=None)
    file = db.Column(db.String(512), nullable=True, default=None)
    line = db.Column(INTEGER(11), nullable=True, default=None)
    code = db.Column(db.String(512), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

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
    __tablename__ = 'projects'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    repository = db.Column(db.String(512), nullable=True, default=None)
    name = db.Column(db.String(50), nullable=True, default=None)
    author = db.Column(db.String(50), nullable=True, default=None)
    remark = db.Column(db.String(50), nullable=True, default=None)
    last_scan = db.Column(db.DateTime, nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, repository, name, author, remark, last_scan, created_at, updated_at):
        self.repository = repository
        self.name = name
        self.author = author
        self.remark = remark
        self.last_scan = last_scan
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraProjects %r - %r>" % (self.id, self.name)


class CobraWhiteList(db.Model):
    __tablename__ = 'whitelist'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    project_id = db.Column(db.Integer, default=None, nullable=True)
    rule_id = db.Column(db.Integer, default=None, nullable=True)
    path = db.Column(db.String(512), default=None, nullable=True)
    reason = db.Column(db.String(512), default=None, nullable=True)
    status = db.Column(TINYINT, default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=None, nullable=True)
    updated_at = db.Column(db.DateTime, default=None, nullable=True)

    def __init__(self, project_id, rule_id, path, reason, status, created_at, updated_at):
        self.project_id = project_id
        self.rule_id = rule_id
        self.path = path
        self.reason = reason
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraWhiteList %r-%r:%r>" % (self.project_id, self.rule_id, self.reason)


class CobraAuth(db.Model):
    __tablename__ = 'auth'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(52), default=None, nullable=True)
    key = db.Column(db.String(256), default=None, nullable=True)
    status = db.Column(TINYINT, default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=None, nullable=True)
    updated_at = db.Column(db.DateTime, default=None, nullable=True)

    def __init__(self, name, key, status, created_at, updated_at):
        self.name = name
        self.key = key
        self.status = status
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraAuth %r-%r>" % (self.name, self.key)


class CobraExt(db.Model):
    __tablename__ = 'ext'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    task_id = db.Column(db.Integer, default=None, nullable=True)
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
    :role: 1-super admin, 2-admin, 3-rule admin
    """
    __tablename__ = 'user'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=None)
    username = db.Column(db.String(64), nullable=True, default=None, unique=True)
    password = db.Column(db.String(256), nullable=True, default=None)
    role = db.Column(TINYINT(2), nullable=True, default=None)
    last_login_time = db.Column(db.DateTime, nullable=True, default=None)
    last_login_ip = db.Column(db.String(16), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, username, password, role, last_login_time, last_login_ip, created_at, updated_at):
        self.username = username
        self.generate_password(password)
        self.role = role
        self.last_login_time = last_login_time
        self.last_login_ip = last_login_ip
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraAdminUser %r-%r>" % (self.username, self.role)

    def verify_password(self, password):
        return check_password_hash(self.password, password)

    def generate_password(self, password):
        self.password = generate_password_hash(password)
