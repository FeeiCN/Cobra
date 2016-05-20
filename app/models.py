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
    scan_type:      scan type, 1-all vulnerabislities, 2-general vulnerabilities, 3-code syntax,
    level:          level, scan level
    scan_way:       scan way, 1-full scan, 2-diff scan
    old_version:    old version, if user select diff scan, this is the old version of the project
    new_version:    new version, if user select diff scan, this is the new version of the project
    '''

    __tablename__ = 'cobra_task_info'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True, nullable=False)
    task_type = db.Column(db.SmallInteger, nullable=False)
    create_time = db.Column(db.Integer, nullable=False)
    filename = db.Column(db.String(255), nullable=True)
    url = db.Column(db.String(255), nullable=True)
    username = db.Column(db.String(255), nullable=True)
    password = db.Column(db.String(255), nullable=True)
    scan_type = db.Column(db.SmallInteger, nullable=False)
    level = db.Column(db.SmallInteger, nullable=False)
    scan_way = db.Column(db.SmallInteger, nullable=False)
    old_version = db.Column(db.String(40), nullable=True)
    new_version = db.Column(db.String(40), nullable=True)

    def __init__(self, task_type, create_time, filename, url, username, password, scan_type, level, scan_way,
                 old_version, new_version):
        self.task_type = task_type
        self.create_time = create_time
        self.filename = filename
        self.url = url
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

