#!/usr/bin/env python2
# coding: utf-8
# file: ValidateClass.py

from functools import wraps

from flask import session, redirect

from DataDictClass import DataDict
from app.controller.backend import ADMIN_URL

__author__ = "lightless"
__email__ = "root@lightless.me"


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
        if not session.get('is_login'):
            return redirect(ADMIN_URL + '/index')
        return f(*args, **kwargs)

    return decorated_function
