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
Document: http://cobra-docs.readthedocs.io

Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.""".format(version=__version__)
__keywords__ = 'cobra, code security'
__epilog__ = """example usage:
  cobra /tmp/need_scan_project_path
  cobra -r /tmp/rule.fei /tmp/project_path
  cobra -f json -o /tmp/report.json /tmp/project_path
  cobra -f json -o feei@feei.cn https://github.com/wufeifei/vc.git
  cobra -f json -o http://push.to.com/api https://github.com/wufeifei/vc.git
"""


# - END META -

def main():
    parser = argparse.ArgumentParser(prog=__program__, usage='%(prog)s [options] <target>', description=__description__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('target', action='store', default='', metavar='<target>', help='file, folder, or repository address')
    parser.add_argument('-r', '--rule', dest='rule', action='store', default='', metavar='<rule_file>', help='specifies the rule configuration file')
    parser.add_argument('-e', '--exclude', dest='exclude', action='store', default='', metavar='<file_or_dir>', help='exclude file or folder')
    parser.add_argument('-f', '--format', dest='format', action='store', default='stream', metavar='<format>', choices=['html', 'json', 'csv', 'xml', 'stream'], help='vulnerability output format (formats: %(choices)s)')
    parser.add_argument('-o', '--output', dest='output', action='store', default='', metavar='<output>', help='vulnerability output FILE, HTTP API URL, MAIL')
    parser.add_argument('-d', '--debug', dest='debug', action='store_true', default=False, help='open debug mode')
    args = parser.parse_args()
    print(args)


if __name__ == '__main__':
    main()
