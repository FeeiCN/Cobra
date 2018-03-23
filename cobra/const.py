# -*- coding: utf-8 -*-

"""
    const
    ~~~~~

    Implements CONSTS

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
access_token = 'YzA4YTVhOTA1ZGExYjg5YTc1ZmI4NmE3MmM3ZjUyNzg2NmRmZmRlNA=='

# Match-Mode
mm_find_extension = 'find-extension'
mm_function_param_controllable = 'function-param-controllable'
mm_regex_param_controllable = 'regex-param-controllable'
mm_regex_only_match = 'regex-only-match'
match_modes = [
    mm_regex_only_match,
    mm_regex_param_controllable,
    mm_function_param_controllable,
    mm_find_extension
]

#
# Function-Param-Controllable
#
# (?:eval|call_function)\s*\((.*)(?:\))
# eval ($test + $test2);
# call_function ($exp);
#
fpc = '(\s*\((.*)(?:\))|\s*(.*\.)*\$.+)'
fpc_single = '[f]{fpc}'.format(fpc=fpc)
fpc_multi = '(?:[f]){fpc}'.format(fpc=fpc)

#
# Find All variables
#
# Hallo $var. blabla $var, $iam a var $varvarvar gfg djf jdfgjh fd $variable $_GET['req']
#
fav = '\$([a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)'
