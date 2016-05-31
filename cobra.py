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
    config = ConfigParser.ConfigParser()
    config.read('config')
    debug = config.get('cobra', 'debug')
    debug = bool(debug)
    web.debug = debug
    manager.run()


if __name__ == '__main__':
    log.info('Starting Cobra...')
    main()
