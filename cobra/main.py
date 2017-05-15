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

__prog__ = 'cobra'
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
  cobra /tmp/project_path -r /tmp/rule.fei
  cobra https://github.com/wufeifei/vc.git -f json -p mail feei@feei.cn
"""


# - END META -

def main():
    parser = argparse.ArgumentParser(prog=__prog__, usage='%(prog)s [options] [target]', description=__description__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument('-e', '--exclude', dest='exclude', action='store', default='', metavar='', help='exclude file or directory')
    parser.add_argument('-r', '--rule', dest='rule', action='store', default='', metavar='', help='specifies the rule configuration file')
    parser.add_argument('-f', '--format', dest='format', action='store', default='json', metavar='', help='vulnerability output format')
    parser.add_argument('-p', '--push', dest='push', action='store', default='', metavar='', help='push vulnerability data')
    parser.add_argument('-d', '--debug', dest='debug', action='store', default='json', metavar='', help='open debug mode')
    args = parser.parse_args()
    print(args)


if __name__ == '__main__':
    main()
