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
from .app import web, manager
from .utils import config
import argparse

__prog__ = 'cobra'
__version__ = '1.2.3'
__author__ = 'Feei'
__contact__ = 'feei@feei.cn'
__homepage__ = 'https://github.com/wufeifei/cobra'
__description__ = 'Cobra is a static code analysis system that automates the detecting vulnerabilities and security issue.'
__keywords__ = 'cobra, code security'
__epilog__ = '---'


# - END META -

def main():
    parser = argparse.ArgumentParser(prog=__prog__, usage='%(prog)s [options] [target]', description=__description__, epilog=__epilog__, version=__version__, formatter_class=argparse.RawDescriptionHelpFormatter)

    debug = config.Config('cobra', 'debug').value
    web.debug = bool(debug)
    manager.run()


if __name__ == '__main__':
    main()
