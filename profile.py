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
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import web

__author__ = "lightless"
__email__ = "root@lightless.me"

web.config['PROFILE'] = True
web.wsgi_app = ProfilerMiddleware(web.wsgi_app, restrictions=[30])
web.run(debug=True)
