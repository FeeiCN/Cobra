#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.report
    ~~~~~~~~~~

    Implements CLI report

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from flask_script import Command, Option


class Report(Command):
    """
    Send report
    Usage:
        python cobra.py report --time=time_time(w/m/q)
    """
    option_list = (
        Option('--time', '-t', dest='t', help='Time e.g. w(weekly)/m(monthly)/q(quarterly)'),
    )

    def run(self, t='w'):
        from scheduler import report
        if t not in ['w', 'm', 'q']:
            print('Error: time type exception')
            return
        if report.Report(t).run():
            print('Report Success')
        else:
            print('Report Failed')
