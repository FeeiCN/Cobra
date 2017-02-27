# -*- coding: utf-8 -*-

"""
    utils.validate
    ~~~~~~~~~~~~~~

    Implements validate

    :author:    Feei <feei@feei.cn>
    :author:    Lightless <root@lightless.me>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from functools import wraps
from flask import session, redirect, request
from utils import config
from app.controller.backend import ADMIN_URL


class DataDict(dict):
    def __init__(self, *args, **kwargs):
        super(DataDict, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(DataDict, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(DataDict, self).__delitem__(key)
        del self.__dict__[key]


class ValidateClass(object):
    def __init__(self, req, *args):
        self.req = req
        self.args = args
        self.vars = DataDict()

    @staticmethod
    def check_login():
        if session.get('is_login') and session.get('is_login') is True:
            return True
        else:
            return False

    def check_args(self):
        for arg in self.args:
            _arg = self.req.form.get(arg)
            if not _arg or _arg == "":
                return False, "".join([arg, ' can not be empty.'])
            else:
                self.vars[arg] = _arg

        return True, None


def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        token = request.args.get('token')
        is_auth_token = token is not None and token == config.Config('cobra', 'secret_key').value
        if not session.get('is_login'):
            if not is_auth_token:
                return redirect(ADMIN_URL + '/index')
        return f(*args, **kwargs)

    return decorated_function
