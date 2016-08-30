#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    profile
    ~~~~~~~

    Implements the profile performance for cobra

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
from werkzeug.contrib.profiler import ProfilerMiddleware
from app import web

__author__ = "lightless"
__email__ = "root@lightless.me"

web.config['PROFILE'] = True
web.wsgi_app = ProfilerMiddleware(web.wsgi_app, restrictions=[30])
web.run(debug=True)
