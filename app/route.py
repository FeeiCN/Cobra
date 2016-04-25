#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#


from app.controller import api
import argparse


def parse_option():
    parser = argparse.ArgumentParser(description='Cobra is a open source Code Security Scan System')
    parser.add_argument('string', metavar='project/path', type=str, nargs='+', help='Project Path')
    parser.add_argument('--version', help='Cobra Version')
    args = parser.parse_args()
    print args.string[0]


def start():
    parse_option()
    api.run()
