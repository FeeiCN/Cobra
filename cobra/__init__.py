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
import argparse
import logging
from cobra.utils.log import logger
from cobra.utils.config import Config
from cobra.app import cli, api

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

GitHub: https://github.com/wufeifei/cobra

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
    # configuration
    Config().initialize()

    # arg parse
    parser = argparse.ArgumentParser(prog=__program__, description=__description__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)

    parser_group_scan = parser.add_argument_group('Scan')
    parser_group_scan.add_argument('-t', '--target', dest='target', action='store', default='', metavar='<target>', help='file, folder, compress, or repository address')
    parser_group_scan.add_argument('-f', '--format', dest='format', action='store', default='json', metavar='<format>', choices=['html', 'json', 'csv', 'xml'], help='vulnerability output format (formats: %(choices)s)')
    parser_group_scan.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='vulnerability output STREAM, FILE, HTTP API URL, MAIL')
    parser_group_scan.add_argument('-r', '--rule', dest='rule', action='store', default='', metavar='<rule_file>', help='specifies the rule configuration file')
    parser_group_scan.add_argument('-e', '--exclude', dest='exclude', action='store', default='', metavar='<file_or_dir>', help='exclude file or folder')
    parser_group_scan.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='open debug mode')

    parser_group_server = parser.add_argument_group('RESTful')
    parser_group_server.add_argument('-H', '--host', dest='host', action='store', default=None, metavar='<host>', help='REST-JSON API Service Host')
    parser_group_server.add_argument('-P', '--port', dest='port', action='store', default=None, metavar='<port>', help='REST-JSON API Service Port')

    args = parser.parse_args()

    if args.debug:
        logger.setLevel(logging.DEBUG)
        logger.debug('set logging level: debug')

    if args.host is None and args.port is None and args.target is '' and args.output is '':
        parser.print_help()
        exit()

    if args.host is not None and args.port is not None:
        logger.info('start RESTful Server...')
        api.start(args.host, args.port, args.debug)
    else:
        logger.info('start scanning...')
        cli.start(args.target, args.format, args.output, args.rule, args.exclude)


if __name__ == '__main__':
    main()
