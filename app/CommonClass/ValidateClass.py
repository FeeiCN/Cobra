#!/usr/bin/env python2
# coding: utf-8
# file: ValidateClass.py

from flask import session

from DataDictClass import DataDict

__author__ = "lightless"
__email__ = "root@lightless.me"


class ValidateClass(object):
    def __init__(self, req, *args):
        self.req = req
        self.args = args
        self.vars = DataDict()

    @staticmethod
    def check_login():
        if session.get('is_login') and session.get('is_login') == True:
            return True
        else:
            return False

    def check_args(self):
        for arg in self.args:
            _arg = self.req.form.get(arg)
            if not _arg or _arg == "":
                return False, arg + ' can not be empty.'
            else:
                self.vars[arg] = _arg

        return True, None

