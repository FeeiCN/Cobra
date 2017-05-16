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
import os
import sys
import argparse
from app import cli, api
import logging
from logging import handlers

logger = logging.getLogger(__name__)

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
except ImportError:
    sh = logging.StreamHandler(sys.stdout)
sh.setFormatter(sh_format)
logger.addHandler(sh)

# file handle
fh = handlers.RotatingFileHandler(logfile, maxBytes=(1048576 * 5), backupCount=7)
fh.setFormatter(fh_format)
logger.addHandler(fh)
logger.setLevel(logging.INFO)

# meta
__program__ = 'cobra'
__version__ = '1.2.3'
__author__ = 'Feei'
__contact__ = 'feei@feei.cn'
__homepage__ = 'https://github.com/wufeifei/cobra'
__description__ = """
    ,---.     |
    |    ,---.|---.,---.,---.
    |    |   ||   ||    ,---|
    `---``---``---``    `---^ v{version}
    
GitHub:   https://github.com/wufeifei/cobra

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.""".format(version=__version__)
__keywords__ = 'cobra, code security'
__epilog__ = """Usage:
  cobra -t /tmp/your_project_path
  cobra -r /tmp/rule.fei -t /tmp/your_project_path
  cobra -f json -o /tmp/report.json -t /tmp/project_path
  cobra -f json -o feei@feei.cn -t https://github.com/wufeifei/vc.git
  cobra -f json -o http://push.to.com/api -t https://github.com/wufeifei/vc.git
  cobra -H 127.0.0.1 -P 80
"""


# - END META -

def main():
    parser = argparse.ArgumentParser(prog=__program__, description=__description__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_scan_group = parser.add_argument_group('Scan')
    parser_scan_group.add_argument('-t', '--target', dest='target', action='store', default='', metavar='<target>', help='file, folder, or repository address')
    parser_scan_group.add_argument('-f', '--format', dest='format', action='store', default='stream', metavar='<format>', choices=['html', 'json', 'csv', 'xml', 'stream'], help='vulnerability output format (formats: %(choices)s)')
    parser_scan_group.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='vulnerability output FILE, HTTP API URL, MAIL')
    parser_scan_group.add_argument('-r', '--rule', dest='rule', action='store', default='', metavar='<rule_file>', help='specifies the rule configuration file')
    parser_scan_group.add_argument('-e', '--exclude', dest='exclude', action='store', default='', metavar='<file_or_dir>', help='exclude file or folder')
    parser_scan_group.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='open debug mode')

    parser_server_group = parser.add_argument_group('RESTful')
    parser_server_group.add_argument('-H', '--host', dest='host', action='store', default=None, metavar='<host>', help='REST-JSON API Service Host')
    parser_server_group.add_argument('-P', '--port', dest='port', action='store', default=None, metavar='<port>', help='REST-JSON API Service Port')

    args = parser.parse_args()

    logger.info('Cobra initialize')
    logger.debug('test')
    if args.debug:
        logger.info('Set debug')
        logger.setLevel(logging.DEBUG)
        logger.debug('ddd')
    if args.host is not None and args.port is not None:
        logger.info('Start RESTful Server...')
        api.start(args.debug, args.host, args.port)
    else:
        logger.info('Start scanning...')
        cli.start(args.target, args.format, args.output, args.rule, args.exclude, args.debug)


if __name__ == '__main__':
    main()
