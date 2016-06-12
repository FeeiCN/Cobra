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
import ConfigParser
from app import web, manager
from utils import log


def main():
    try:
        config = ConfigParser.ConfigParser()
        config.read('config')
        debug = config.get('cobra', 'debug')
        debug = bool(debug)
    except ConfigParser.Error:
        debug = True
        log.critical("/config File Not Found, copy config.example to config please!")
    web.debug = debug
    log.info('Starting Cobra Engine...')
    manager.run()


if __name__ == '__main__':
    main()
