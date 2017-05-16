# -*- coding: utf-8 -*-

"""
    utils.log
    ~~~~~~~~~

    Implements log initialize

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import sys
import logging
from logging import handlers

logger = logging.getLogger(__name__)


def init_log():
    logs_directory = os.path.join(os.path.expandvars(os.path.expanduser("~")), ".cobra")
    if os.path.isdir(logs_directory) is not True:
        os.mkdir(logs_directory)
    logfile = os.path.join(logs_directory, 'cobra.log')
    fh_format = logging.Formatter("[%(asctime)s] %(levelname)s [%(name)s:%(lineno)s] %(message)s")
    sh_format = logging.Formatter("\r[%(asctime)s] [%(levelname)s] %(message)s", "%H:%M:%S")

    # stream handle
    try:
        from utils.csh import ColorizingStreamHandler

        sh = ColorizingStreamHandler(sys.stdout)
        sh.level_map[logging.getLevelName("PAYLOAD")] = (None, "cyan", False)
        sh.level_map[logging.getLevelName("TRAFFIC OUT")] = (None, "magenta", False)
        sh.level_map[logging.getLevelName("TRAFFIC IN")] = ("magenta", None, False)
    except ImportError:
        sh = logging.StreamHandler(sys.stdout)
    sh.setFormatter(sh_format)
    logger.addHandler(sh)

    # file handle
    fh = handlers.RotatingFileHandler(logfile, maxBytes=(1048576 * 5), backupCount=7)
    fh.setFormatter(fh_format)
    logger.addHandler(fh)
    logger.setLevel(logging.INFO)
    return logger, logging
