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


class Whitelist(db.Model):
    id = db.Cloum(db.Integer, primary_key=True)
    url = db.Column(db.String(256))
    remark = db.Column(db.String(56))
    status = db.Column(db.Integer(2))

    def __repr__(self):
        return self.url
