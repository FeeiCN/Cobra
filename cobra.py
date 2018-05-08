#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra entry

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/FeeiCN/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import re
import sys
import os

if __name__ == '__main__':
    sys.argv[0] = re.sub(r'(-script\.pyw?|\.exe)?$', '', sys.argv[0])
    try:
        os.system('git pull')
    except:
        pass
    finally:
        from cobra import main
        sys.exit(main())
