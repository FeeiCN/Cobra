# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from phply.phplex import lexer  # 词法分析
from phply.phpparse import make_parser  # 语法分析
from phply import phpast as php

with_line = True


def export(items):
    result = []
    if items:
        for item in items:
            if hasattr(item, 'generic'):
                item = item.generic(with_lineno=with_line)
            result.append(item)
    return result


def get_all_params(nodes):  # 用来获取调用函数的参数列表，nodes为参数列表
    params = []
    for node in nodes:
        if isinstance(node.node, php.Variable):
            params.append(node.node.name)
    return params


def get_expr_name(node):  # expr为'expr'中的值
    param_lineno = 0
    if isinstance(node, php.ArrayOffset):  # 当赋值表达式为数组
        param_expr = get_node_name(node.node)  # 返回数组名
        param_lineno = node.node.lineno

    elif isinstance(node, php.Variable):  # 当赋值表达式为变量
        param_expr = node.name  # 返回变量名
        param_lineno = node.lineno

    elif isinstance(node, php.FunctionCall):  # 当赋值表达式为函数
        param_expr = get_all_params(node.params)  # 返回函数参数列表
        param_lineno = node.lineno

    else:
        param_expr = node

    return param_expr, param_lineno


def get_node_name(node):  # node为'node'中的元组
    if isinstance(node, php.Variable):
        return node.name  # 返回此节点中的变量名


def get_functioncall_params(node):  # functioncall为'functioncall'中的字典{'lineno', 'name':函数名, 'params':参数列表}
    all_params = []
    if 'params' in node:
        params = node['params']  # params包含所有参数的一个列表
        for method, value in params:  # param为每一个参数的元组
            if method == 'Parameter':
                param = get_node_name(value['node'])
                all_params.append(param)
    return all_params


def get_assignment_params(node):  # assignment为'Assignment'中的字典{'expr':表达式为赋值来源, 'is_ref', 'lineno', 'node'}
    if 'expr' in node:
        pass


def is_controllable(expr):  # 获取表达式中的变量，看是否在用户可控变量列表中
    """
    判断赋值表达式是否是用户可控的
    :param expr:
    :return:
    """
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
    if expr in controlled_params:
        return True, expr
    return False, None


def parameters_back(param, nodes):  # 用来得到回溯过程中的被赋值的变量是否与敏感函数变量相等,param是当前需要跟踪的污点
    """
    递归回溯敏感函数的赋值流程，param为跟踪的污点
    :param param:
    :param nodes:
    :return:
    """
    is_co = False
    cp = None
    if len(nodes) != 0:
        node = nodes[len(nodes) - 1]

        if isinstance(node, php.Assignment):
            param_node = get_node_name(node.node)  # param_node为被赋值的变量
            param_expr, expr_lineno = get_expr_name(node.expr)  # param_expr为赋值表达式,param_expr为变量或者列表

            if param == param_node and not isinstance(param_expr, list):  # 找到变量的来源，开始继续分析变量的赋值表达式是否可控
                is_co, cp = is_controllable(param_expr)  # 开始判断变量是否可控
                param = param_expr  # 每次找到一个污点的来源时，开始跟踪新污点，覆盖旧污点
                if is_co is True:
                    print "[USAGE-CONTROLLABLE] {cp} in line {expr_lineno}".format(cp=cp, expr_lineno=expr_lineno)

            if is_co is False:  # 当is_co为True时找到可控，停止递归
                is_co, cp = parameters_back(param, nodes[:-1])  # 找到可控的输入时，停止递归

            if param == param_node and isinstance(param_expr, list):
                for expr in param_expr:
                    param = expr
                    _is_co, _cp = parameters_back(param, nodes[:-1])  # 分别对函数参数递归，获取其返回值
                    if _is_co is True:  # 当参数可控时，值赋给is_co 和 cp
                        is_co = _is_co
                        cp = _cp

    return is_co, cp


def analysis(nodes, vul_function):
    """
    找到敏感函数调用点-->取出敏感函数的参数-->循环判断参数是否可控
    :param nodes: 所有节点
    :param vul_function: 要判断的敏感函数名
    :return:
    """
    back_node = []
    for node in nodes:
        if isinstance(node, php.FunctionCall):
            if node.name == vul_function:  # 定位到敏感函数
                params = get_all_params(node.params)  # 开始取敏感函数中的参数列表
                for param in params:
                    is_co, cp = parameters_back(param, back_node)
                    if is_co is True:
                        print "[WARNING]The parameters '{param}' from function '{function}' are controllable in " \
                              "line {line}".format(param=param, function=node.name, line=node.lineno)
                        print "------"

        else:
            back_node.append(node)


def scan(code_content, sensitive_func):
    """
    开始检测函数
    :param code_content: 要检测的文件内容
    :param sensitive_func: 要检测的敏感函数
    :return:
    """
    parser = make_parser()
    all_nodes = parser.parse(code_content, debug=False, lexer=lexer.clone(), tracking=with_line)
    for func in sensitive_func:  # 循环判断代码中是否存在敏感函数，若存在，递归判断参数是否可控
        analysis(all_nodes, func)


code_contents = """<?php
$e = $_GET['test'];
$c = b($e);
$cmd = a($c, $test, $b);
$cmd1 = $e;
$cmd2 = $e;
system($cmd,$cmd1);
shell_exec($cmd);
"""

F_EXECS = [  # 命令执行的敏感函数
    'backticks',
    'exec',
    'expect_popen',
    'passthru',
    'pcntl_exec',
    'popen',
    'proc_open',
    'shell_exec',
    'system',
    'mail',
    'mb_send_mail',
    'w32api_invoke_function',
    'w32api_register_function',
]

scan(code_contents, F_EXECS)
