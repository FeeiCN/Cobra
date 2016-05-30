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

from sqlalchemy.dialects.mysql import TINYINT, INTEGER

from app import db


# task_info table. store task information.
class CobraTaskInfo(db.Model):
    '''
    id:             task id
    task_type:      task type, 1-login to gitlab with username and password, 2-upload file
    create_time:    task created time
    filename:       filename, if user upload source code, this is the archive filename
    url:            url, if user provide gitlab account, this is the project url on gitlab
    username:       username, gitlab username
    password:       password, gitlab password
    scan_type:      scan type, 1-all vulnerabilities, 2-general vulnerabilities, 3-code syntax,
    level:          level, scan level
    scan_way:       scan way, 1-full scan, 2-diff scan
    old_version:    old version, if user select diff scan, this is the old version of the project
    new_version:    new version, if user select diff scan, this is the new version of the project
    '''

    __tablename__ = 'cobra_task_info'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    task_type = db.Column(db.SmallInteger, nullable=False)
    create_time = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    branch = db.Column(db.String(64), nullable=True)
    username = db.Column(db.String(64), nullable=True)
    password = db.Column(db.String(64), nullable=True)
    scan_type = db.Column(db.SmallInteger, nullable=False)
    level = db.Column(db.SmallInteger, nullable=False)
    scan_way = db.Column(db.SmallInteger, nullable=False)
    old_version = db.Column(db.String(40), nullable=True)
    new_version = db.Column(db.String(40), nullable=True)

    def __init__(self, task_type, create_time, filename, url, branch, username, password, scan_type, level, scan_way,
                 old_version, new_version):
        self.task_type = task_type
        self.create_time = create_time
        self.filename = filename
        self.url = url
        self.branch = branch
        self.username = username
        self.password = password
        self.scan_type = scan_type
        self.level = level
        self.scan_way = scan_way
        self.old_version = old_version
        self.new_version = new_version

    def __repr__(self):
        return '<task_info %r - %r>' % (self.id,
                                        "username/password on gitlab" if self.scan_type == 1 else "file upload")


class CobraRules(db.Model):
    __tablename__ = 'rules'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    vul_id = db.Column(TINYINT(unsigned=False), nullable=True, default=None)
    language = db.Column(TINYINT(unsigned=False), nullable=True, default=None)
    regex = db.Column(db.String(512), nullable=True, default=None)
    description = db.Column(db.String(256), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, vul_id, language, regex, description, created_at, updated_at):
        self.vul_id = vul_id
        self.language = language
        self.regex = regex
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraRules %r - %r: %r>" % (self.id, self.language, self.regex)


class CobraVuls(db.Model):
    __tablename__ = 'vuls'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(56), nullable=True, default=None)
    description = db.Column(db.String(512), nullable=True, default=None)
    created_at = db.Column(db.DateTime, nullable=True, default=None)
    updated_at = db.Column(db.DateTime, nullable=True, default=None)

    def __init__(self, name, description, created_at, updated_at):
        self.name = name
        self.description = description
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraVuls %r - %r>" % (self.id, self.name)


class CobraSupportLanguage(db.Model):
    __tablename__ = 'languages'
    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    language = db.Column(db.String(32), nullable=False)
    suffix = db.Column(db.String(256), nullable=False)

    def __init__(self, language, suffix):
        self.language = language
        self.suffix = suffix

    def __repr__(self):
        return "<CobraSupportLanguage %r - %r>" % (self.id, self.language)


class CobraProject(db.Model):

    __tablename__ = 'projects'

    id = db.Column(INTEGER(unsigned=True), primary_key=True, autoincrement=True, nullable=False)
    name = db.Column(db.String(128), default=None, nullable=True)
    repo_type = db.Column(TINYINT(2), nullable=False)
    repository = db.Column(db.String(256), default=None, nullable=True)
    branch = db.Column(db.String(128), default=None, nullable=True)
    username = db.Column(db.String(128), default=None, nullable=True)
    password = db.Column(db.String(128), default=None, nullable=True)
    scan_at = db.Column(db.DateTime, default=None, nullable=True)
    created_at = db.Column(db.DateTime, default=None, nullable=True)
    updated_at = db.Column(db.DateTime, default=None, nullable=True)

    def __init__(self, name, repo_type, repository, branch, username, password, scan_at, created_at, updated_at):
        self.name = name
        self.repo_type = repo_type
        self.repository = repository
        self.branch = branch
        self.username = username
        self.password = password
        self.scan_at = scan_at
        self.created_at = created_at
        self.updated_at = updated_at

    def __repr__(self):
        return "<CobraProject %r>" % self.repository




