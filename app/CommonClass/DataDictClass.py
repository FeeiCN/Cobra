#!/usr/bin/env python2
# coding: utf-8
# file: DataDictClass


__author__ = "lightless"
__email__ = "root@lightless.me"


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

