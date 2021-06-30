# -*- coding: utf-8 -*-

"""
    tests.pickup
    ~~~~~~~~~~~~

    Tests cobra.pickup

    :author:    banbooboo <1798736436@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""

from cobra.pickup import Directory
import os

def test_vulnerabilities():


    dt =Directory(os.path.dirname(__file__)+"/vulnerabilities")

    assert dt.collect_files()