#!/usr/bin/env python

from app import web

# default admin url
admin_url = '/admin'


@web.route(admin_url+'/', methods=['GET'])
@web.route(admin_url+'/index', methods=['GET'])
def index():
    return '123'

