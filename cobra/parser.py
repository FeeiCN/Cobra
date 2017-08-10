# -*- coding: utf-8 -*-

"""
    parser
    ~~~~~~

    Implements parser

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from phply.phplex import lexer
from phply.phpparse import make_parser

with_lineno = True


def export(items):
    result = []
    if items:
        for item in items:
            if hasattr(item, 'generic'):
                item = item.generic(with_lineno=with_lineno)
            result.append(item)
    return result


def get_all_params_parent(node_node):
    _params = []

    def get_all_params(node_node):
        if node_node[0] == 'Variable':
            _params.append(node_node[1]['name'])
        else:
            for k, v in node_node[1].items():
                if isinstance(v, tuple):
                    get_all_params(v)

    get_all_params(node_node)
    return _params


def get_all_parameter(node_params):
    params = []
    for x in node_params:
        if x[0] == 'Parameter':
            params = params + get_all_params_parent(x[1]['node'])
    return params


def is_controllable(expr):
    # 0 'expr': ('ArrayOffset',)
    # 1 {'lineno': 3, 'node': ('Variable', {'lineno': 3, 'name': '$_GET'}), 'expr': 'cmd'}
    controllabled_params = [
        '$_GET',
        '$_POST'
    ]
    controllable_params = get_all_params_parent(expr[1]['node'])
    for cp in controllable_params:
        if cp in controllabled_params:
            return True, cp
    return False, None


def get_all_usage_controllable(params, nodes):
    """get all params usage and is controllable"""
    result = {}
    for method, value in nodes:
        if method == 'Assignment':
            usage_params = get_all_params_parent(value['node'])
            for up in usage_params:
                if up in params:
                    # check controllable
                    ic, cf = is_controllable(value['expr'])
                    result[up] = {
                        'ic': ic,
                        'cf': cf
                    }
    return result


def traversal(nodes, vul_function, vul_function_line, level=0):
    for method, value in nodes:
        if method == 'FunctionCall':
            if value['name'] == vul_function and value['lineno'] == vul_function_line:
                print('[FUNCTION] ', level, method, value['name'])
                params = get_all_parameter(value['params'])
                print('[PARAMS]', params)
                usage_controllable = get_all_usage_controllable(params, nodes)
                print('[USAGE-CONTROLLABLE]', usage_controllable)
                print('----------')
        if 'nodes' in value:
            traversal(value['nodes'], vul_function, vul_function_line, level=level + 1)
        print(method, value)


def scan(code_content, vul_function, vul_function_line):
    parser = make_parser()
    all_nodes = export(parser.parse(code_content, debug=False, lexer=lexer.clone(), tracking=with_lineno))
    print(all_nodes)
    traversal(all_nodes, vul_function, vul_function_line)


if __name__ == '__main__':
    tests = [
        (u"""<?php
    $cmd = $_GET['cmd'];
    system("ls" + $cmd);
    """, u'system', 3),
        (u"""<?php
    $cmd_test = $_POST['cmd'];
    exec("test" + $cmd_test);
    """, u'exec', 3),
    ]
    for test in tests:
        test_content, func, line = test
        print(test)
        scan(test_content, func, line)
