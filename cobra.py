#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
from app import web, manager
from utils import log, config


def main():
    log.Log()
    debug = config.Config('cobra', 'debug').value
    web.debug = int(debug)
    manager.run()


if __name__ == '__main__':
    main()
