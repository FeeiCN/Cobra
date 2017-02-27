# -*- coding: utf-8 -*-

"""
    utils.tool
    ~~~~~~~~~~

    Third-party tool

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import sys
import os
import logging

logging = logging.getLogger(__name__)

# `grep` (`ggrep` on Mac)
grep = '/bin/grep'
# `find` (`gfind` on Mac)
find = '/bin/find'

if 'darwin' == sys.platform:
    ggrep = ''
    gfind = ''
    for root, dir_names, file_names in os.walk('/usr/local/Cellar/grep'):
        for filename in file_names:
            if 'ggrep' == filename or 'grep' == filename:
                ggrep = os.path.join(root, filename)
    for root, dir_names, file_names in os.walk('/usr/local/Cellar/findutils'):
        for filename in file_names:
            if 'gfind' == filename:
                gfind = os.path.join(root, filename)
    if ggrep == '':
        logging.critical("brew install ggrep pleases!")
        sys.exit(0)
    else:
        grep = ggrep
    if gfind == '':
        logging.critical("brew install findutils pleases!")
        sys.exit(0)
    else:
        find = gfind
