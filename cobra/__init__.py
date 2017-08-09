#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
<<<<<<< HEAD
=======
import sys
>>>>>>> upstream/master
import time
import argparse
import logging
from .log import logger
from . import cli, api, config

from .__version__ import __title__, __introduction__, __url__, __version__
<<<<<<< HEAD
from .__version__ import __build__, __author__, __author_email__, __license__
from .__version__ import __copyright__, __epilog__

=======
from .__version__ import __author__, __author_email__, __license__
from .__version__ import __copyright__, __epilog__

try:
    reload(sys)
    sys.setdefaultencoding('utf-8')
except NameError as e:
    pass

>>>>>>> upstream/master

def main():
    # arg parse
    t1 = time.clock()
<<<<<<< HEAD
    parser = argparse.ArgumentParser(prog=__title__, description=__introduction__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)
=======
    parser = argparse.ArgumentParser(prog=__title__, description=__introduction__, epilog=__epilog__, formatter_class=argparse.RawDescriptionHelpFormatter)
>>>>>>> upstream/master

    parser_group_scan = parser.add_argument_group('Scan')
    parser_group_scan.add_argument('-t', '--target', dest='target', action='store', default='', metavar='<target>', help='file, folder, compress, or repository address')
    parser_group_scan.add_argument('-f', '--format', dest='format', action='store', default='json', metavar='<format>', choices=['html', 'json', 'csv', 'xml'], help='vulnerability output format (formats: %(choices)s)')
    parser_group_scan.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='vulnerability output STREAM, FILE, HTTP API URL, MAIL')
    parser_group_scan.add_argument('-r', '--rule', dest='special_rules', action='store', default=None, metavar='<rule_id>', help='specifies rules e.g: CVI-100001,cvi-190001')
    parser_group_scan.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='open debug mode')
    parser_group_scan.add_argument('-sid', '--sid', dest='sid', action='store', default=None, help='scan id(API)')

    parser_group_server = parser.add_argument_group('RESTful')
    parser_group_server.add_argument('-H', '--host', dest='host', action='store', default=None, metavar='<host>', help='REST-JSON API Service Host')
    parser_group_server.add_argument('-P', '--port', dest='port', action='store', default=None, metavar='<port>', help='REST-JSON API Service Port')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
<<<<<<< HEAD
        logger.debug('set logging level: debug')
=======
        logger.debug('[INIT] set logging level: debug')
>>>>>>> upstream/master

    if args.host is None and args.port is None and args.target is '' and args.output is '':
        parser.print_help()
        exit()

    if args.host is not None and args.port is not None:
<<<<<<< HEAD
        logger.debug('start RESTful Server...')
        api.start(args.host, args.port, args.debug)
    else:
        logger.debug('start scanning...')
        cli.start(args.target, args.format, args.output, args.special_rules, args.sid)
    t2 = time.clock()
    logger.info('Done! TC:{TC}s'.format(TC=t2 - t1))
=======
        logger.debug('[INIT] start RESTful Server...')
        api.start(args.host, args.port, args.debug)
    else:
        logger.debug('[INIT] start scanning...')
        cli.start(args.target, args.format, args.output, args.special_rules, args.sid)
    t2 = time.clock()
    logger.info('[INIT] Done! TC:{TC}s'.format(TC=t2 - t1))
>>>>>>> upstream/master


if __name__ == '__main__':
    main()
