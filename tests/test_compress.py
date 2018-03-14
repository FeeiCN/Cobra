# -*- coding: utf-8 -*-

"""
    tests.test_compress
    ~~~~~~~~~~~~~~~~~~~

    Tests pickup.compress

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import pytest
from cobra.pickup import Decompress


def test_not_support_extension():
    with pytest.raises(IOError):
        assert Decompress('test.tar.xyz').decompress()
