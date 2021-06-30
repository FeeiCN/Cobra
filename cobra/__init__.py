#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import sys
import time
import argparse
import logging
import traceback
import platform
from .log import logger
from . import cli, api, config
from .cli import get_sid
from .engine import Running
from .utils import unhandled_exception_message, create_github_issue, set_config_hash, get_config_hash
from .report import Report

from .__version__ import __title__, __introduction__, __url__, __version__
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__, __epilog__

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError as e:
    pass


def main():
    try:
        # arg parse
        t1 = time.time()
        parser = argparse.ArgumentParser(prog=__title__, description=__introduction__, epilog=__epilog__, formatter_class=argparse.RawDescriptionHelpFormatter)

        parser_group_scan = parser.add_argument_group('Scan')
        parser_group_scan.add_argument('-t', '--target', dest='target', action='store', default='', metavar='<target>', help='file, folder, compress, or repository address')
        parser_group_scan.add_argument('-f', '--format', dest='format', action='store', default='json', metavar='<format>', choices=['json', 'csv', 'xml'], help='vulnerability output format (formats: %(choices)s)')
        parser_group_scan.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='vulnerability output STREAM, FILE, HTTP API URL, MAIL')
        parser_group_scan.add_argument('-r', '--rule', dest='special_rules', action='store', default=None, metavar='<rule_id>', help='specifies rules e.g: CVI-100001,cvi-190001')
        parser_group_scan.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='open debug mode')
        parser_group_scan.add_argument('-sid', '--sid', dest='sid', action='store', default=None, help='scan id(API)')
        parser_group_scan.add_argument('-dels', '--dels', dest='dels', action='store_true', default=False, help='del target directory True or False')
        parser_group_scan.add_argument('-rp', '--report', dest='report', action='store_true', default=False, help='automation report Cobra data')
        parser_group_scan.add_argument('-m', '--md5', dest='md5', action='store_true', default=False, help='Create projects file md5')

        parser_group_server = parser.add_argument_group('RESTful')
        parser_group_server.add_argument('-H', '--host', dest='host', action='store', default=None, metavar='<host>', help='REST-JSON API Service Host')
        parser_group_server.add_argument('-P', '--port', dest='port', action='store', default=None, metavar='<port>', help='REST-JSON API Service Port')

        args = parser.parse_args()

        if args.debug:
            logger.setLevel(logging.DEBUG)
            logger.debug('[INIT] set logging level: debug')

        if args.report:
            logger.info('[REPORT] Start report')
            res = Report().run()
            if res is False:
                logger.critical('[REPORT] Cobra Report failed')
            else:
                logger.info('[REPORT] Cobra Report Success ')
            exit()

        if args.md5 and args.port is None and args.host is None and args.target is '':
            set_config_hash()
            exit()

        if args.host is None and args.port is None and args.target is '' and args.output is '':
            parser.print_help()
            exit()

        if 'windows' in platform.platform().lower():
            logger.critical('Nonsupport Windows!!!')

        if args.host is not None and args.port is not None:
            try:
                if not int(args.port) <= 65535:
                    logger.critical('port must be 0-65535.')
                    exit()
            except ValueError as e:
                logger.critical('port must be 0-65535')
                exit()
            logger.debug('[INIT] start RESTful Server...')
            api.start(args.host, args.port, args.debug)
        else:
            logger.debug('[INIT] start scanning...')

            # Native CLI mode
            if args.sid is None:
                a_sid = get_sid(args.target, True)
                data = {
                    'status': 'running',
                    'report': ''
                }
                Running(a_sid).status(data)
            else:
                # API call CLI mode
                a_sid = args.sid
            cli.start(args.target, args.format, args.output, args.special_rules, a_sid, args.dels)
        t2 = time.time()
        logger.info('[INIT] Done! Consume Time:{ct}s'.format(ct=t2 - t1))

    except Exception as e:
        err_msg = unhandled_exception_message()
        exc_msg = traceback.format_exc()
        logger.warning(exc_msg)
        if get_config_hash():  # 项目未被修改，提交issue
            create_github_issue(err_msg, exc_msg)


if __name__ == '__main__':
    main()
