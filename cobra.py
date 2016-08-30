#!/usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright 2016 Feei. All Rights Reserved
#
# :author:   Feei <wufeifei@wufeifei.com>
# :homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'docs/COPYING' for copying permission
#
from app import web, manager
from utils import config


def main():
    debug = config.Config('cobra', 'debug').value
    web.debug = bool(debug)
    manager.run()


if __name__ == '__main__':
    main()
