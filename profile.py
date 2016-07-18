#!/usr/bin/env python2
# coding: utf-8
# file: profile.py

from werkzeug.contrib.profiler import ProfilerMiddleware
from app import web

__author__ = "lightless"
__email__ = "root@lightless.me"

web.config['PROFILE'] = True
web.wsgi_app = ProfilerMiddleware(web.wsgi_app, restrictions=[30])
web.run(debug=True)
