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
import ConfigParser

import sqlalchemy

from app.controller import api


def start():
    # API
    api.run()
    config = ConfigParser.ConfigParser()
    config.read('config')
    print config.get('mysql', 'username')
    db = sqlalchemy.create_engine('mysql+mysqldb://root:@127.0.0.1:3306/cobra', echo=True)
