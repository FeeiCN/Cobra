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
from .log import logger
from phply.phplex import lexer
from phply.phpparse import make_parser

with_line = True


def export(items):
    result = []
    if items:
        for item in items:
            if hasattr(item, 'generic'):
                item = item.generic(with_lineno=with_line)
            result.append(item)
    return result


def get_all_params_parent(node_node):
    _params = []

    def get_all_params(nn):
        if nn[0] == 'Variable':
            _params.append(nn[1]['name'])
        else:
            for k, v in nn[1].items():
                if isinstance(v, tuple):
                    get_all_params(v)

    get_all_params(node_node)
    return _params


def get_all_parameter(node_params):
    """
    取函数所有入参名称
    :param node_params:
    :return:
    """
    params = []
    for x in node_params:
        if x[0] == 'Parameter':
            params = params + get_all_params_parent(x[1]['node'])
    return params


def is_controllable(expr):
    controlled_params = [
        '$_GET',
        '$_POST',
        '$_REQUEST',
        '$_COOKIE',
        '$_FILES',
        '$_SERVER',
        '$HTTP_POST_FILES',
        '$HTTP_COOKIE_VARS',
        '$HTTP_REQUEST_VARS',
        '$HTTP_POST_VARS',
        '$HTTP_RAW_POST_DATA',
        '$HTTP_GET_VARS'
    ]
    if 'node' in expr[1]:
        controllable_params = get_all_params_parent(expr[1]['node'])
        for cp in controllable_params:
            if cp in controlled_params:
                return True, cp
    return False, None


def get_all_usage_controllable(params, nodes):
    """
    遍历所有节点，判断是否有函数入参的赋值情况
    :param params: 函数所有入参
    :param nodes: 全部节点
    :return:
    """
    result = {}
    for method, value in nodes:
        if method == 'Assignment':
            usage_params = get_all_params_parent(value['node'])
            for up in usage_params:
                # check controllable
                ic, cf = is_controllable(value['expr'])
                logger.debug('[PARAM-ASSIGN] {l} {p} = {a}'.format(l=value['lineno'], p=usage_params, a=cf))
                in_params = False
                if up in params:
                    in_params = True
                    result[up] = {
                        'ic': ic,
                        'cf': cf
                    }
                    # if in_params is False:
                    #     logger.debug('digui')
                    #     get_all_usage_controllable(usage_params, nodes)
        else:
            logger.debug('not assignment')
    return result


def traversal(nodes, vul_function, vul_function_line, level=0):
    """
    递归所有节点，找到函数调用点 -> 取出所有参数变量 -> 判断每一个入参变量是否可控
    :param nodes:
    :param vul_function:
    :param vul_function_line:
    :param level:
    :return:
    """
    func, params, uc = None, None, None
    for method, value in nodes:
        logger.debug('[LINE] {m} {v}'.format(m=method, v=value))
        if method == 'FunctionCall':
            if value['name'] == vul_function and value['lineno'] == vul_function_line:
                func = value['name']
                logger.debug('[FUNCTION] {l} {m} {f}'.format(l=level, m=method, f=func))
                params = get_all_parameter(value['params'])
                logger.debug('[PARAMS] {p}'.format(p=params))
                uc = get_all_usage_controllable(params, nodes)
                logger.debug('[USAGE-CONTROLLABLE] {uc}'.format(uc=uc))
                logger.debug('----------')
        if 'nodes' in value:
            traversal(value['nodes'], vul_function, vul_function_line, level=level + 1)
    return func, params, uc


def scan(code_content, vul_function, vul_function_line):
    parser = make_parser()
    all_nodes = export(parser.parse(code_content, debug=False, lexer=lexer.clone(), tracking=with_line))
    return traversal(all_nodes, vul_function, vul_function_line)
