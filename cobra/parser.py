# -*- coding: utf-8 -*-

"""
    parser
    ~~~~~~

    Implements Code Parser

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from phply.phplex import lexer  # 词法分析
from phply.phpparse import make_parser  # 语法分析
from phply import phpast as php
from .log import logger

with_line = True
scan_results = []  # 结果存放列表初始化
repairs = []  # 用于存放修复函数


def export(items):
    result = []
    if items:
        for item in items:
            if hasattr(item, 'generic'):
                item = item.generic(with_lineno=with_line)
            result.append(item)
    return result


def export_list(params, export_params):
    """
    将params中嵌套的多个列表，导出为一个列表
    :param params:
    :param export_params:
    :return:
    """
    for param in params:
        if isinstance(param, list):
            export_params = export_list(param, export_params)

        else:
            export_params.append(param)

    return export_params


def get_all_params(nodes):  # 用来获取调用函数的参数列表，nodes为参数列表
    """
    获取函数结构的所有参数
    :param nodes:
    :return:
    """
    params = []
    export_params = []  # 定义空列表，用来给export_list中使用
    for node in nodes:
        if isinstance(node.node, php.FunctionCall):  # 函数参数来自另一个函数的返回值
            params = get_all_params(node.node.params)

        else:
            if isinstance(node.node, php.Variable):
                params.append(node.node.name)

            if isinstance(node.node, php.BinaryOp):
                params = get_binaryop_params(node.node)
                params = export_list(params, export_params)

            if isinstance(node.node, php.ArrayOffset):
                param = get_node_name(node.node.node)
                params.append(param)

            if isinstance(node.node, php.Cast):
                param = get_cast_params(node.node.expr)
                params.append(param)

            if isinstance(node.node, php.Silence):
                param = get_silence_params(node.node)
                params.append(param)

    return params


def get_silence_params(node):
    """
    用来提取Silence类型中的参数
    :param node:
    :return:
    """
    param = []
    if isinstance(node.expr, php.Variable):
        param = get_node_name(node.expr)

    if isinstance(node.expr, php.FunctionCall):
        param.append(node.expr)

    if isinstance(node.expr, php.Eval):
        param.append(node.expr)

    if isinstance(node.expr, php.Assignment):
        param.append(node.expr)

    return param


def get_cast_params(node):
    """
    用来提取Cast类型中的参数
    :param node:
    :return:
    """
    param = []
    if isinstance(node, php.Silence):
        param = get_node_name(node.expr)

    return param


def get_binaryop_params(node):  # 当为BinaryOp类型时，分别对left和right进行处理，取出需要的变量
    """
    用来提取Binaryop中的参数
    :param node:
    :return:
    """
    logger.debug('[AST] Binaryop --> {node}'.format(node=node))
    params = []
    buffer_ = []

    if isinstance(node.left, php.Variable) or isinstance(node.right, php.Variable):  # left, right都为变量直接取值
        if isinstance(node.left, php.Variable):
            params.append(node.left.name)

        if isinstance(node.right, php.Variable):
            params.append(node.right.name)

    if not isinstance(node.right, php.Variable) or not isinstance(node.left, php.Variable):  # right不为变量时
        params_right = get_binaryop_deep_params(node.right, params)
        params_left = get_binaryop_deep_params(node.left, params)

        params = params_left + params_right

    params = export_list(params, buffer_)
    return params


def get_binaryop_deep_params(node, params):  # 取出right，left不为变量时，对象结构中的变量
    """
    取出深层的变量名
    :param node: node为上一步中的node.left或者node.right节点
    :param params:
    :return:
    """
    if isinstance(node, php.ArrayOffset):  # node为数组，取出数组变量名
        param = get_node_name(node.node)
        params.append(param)

    if isinstance(node, php.BinaryOp):  # node为BinaryOp，递归取出其中变量
        param = get_binaryop_params(node)
        params.append(param)

    if isinstance(node, php.FunctionCall):  # node为FunctionCall，递归取出其中变量名
        params = get_all_params(node.params)

    return params


def get_expr_name(node):  # expr为'expr'中的值
    """
    获取赋值表达式的表达式部分中的参数名-->返回用来进行回溯
    :param node:
    :return:
    """
    param_lineno = 0
    is_re = False
    if isinstance(node, php.ArrayOffset):  # 当赋值表达式为数组
        param_expr = get_node_name(node.node)  # 返回数组名
        param_lineno = node.node.lineno

    elif isinstance(node, php.Variable):  # 当赋值表达式为变量
        param_expr = node.name  # 返回变量名
        param_lineno = node.lineno

    elif isinstance(node, php.FunctionCall):  # 当赋值表达式为函数
        param_expr = get_all_params(node.params)  # 返回函数参数列表
        param_lineno = node.lineno
        is_re = is_repair(node.name)  # 调用了函数，判断调用的函数是否为修复函数

    elif isinstance(node, php.BinaryOp):  # 当赋值表达式为BinaryOp
        param_expr = get_binaryop_params(node)
        param_lineno = node.lineno

    else:
        param_expr = node

    return param_expr, param_lineno, is_re


def get_node_name(node):  # node为'node'中的元组
    """
    获取Variable类型节点的name
    :param node:
    :return:
    """
    if isinstance(node, php.Variable):
        return node.name  # 返回此节点中的变量名


def is_repair(expr):
    """
    判断赋值表达式是否出现过滤函数，如果已经过滤，停止污点回溯，判定漏洞已修复
    :param expr: 赋值表达式
    :return:
    """
    is_re = False  # 是否修复，默认值是未修复
    for repair in repairs:
        if expr == repair:
            is_re = True
            return is_re
    return is_re


def is_sink_function(param_expr, function_params):
    """
    判断自定义函数的入参-->判断此函数是否是危险函数
    :param param_expr:
    :param function_params:
    :return:
    """
    is_co = -1
    cp = None
    if function_params is not None:
        for function_param in function_params:
            if param_expr == function_param:
                is_co = 2
                cp = function_param
                logger.debug('[AST] is_sink_function --> {function_param}'.format(function_param=cp))
    return is_co, cp


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
        logger.debug('[AST] is_controllable --> {expr}'.format(expr=expr))
        return 1, expr
    return -1, None


def parameters_back(param, nodes, function_params=None):  # 用来得到回溯过程中的被赋值的变量是否与敏感函数变量相等,param是当前需要跟踪的污点
    """
    递归回溯敏感函数的赋值流程，param为跟踪的污点，当找到param来源时-->分析复制表达式-->获取新污点；否则递归下一个节点
    :param param:
    :param nodes:
    :param function_params:
    :return:
    """
    expr_lineno = 0  # source所在行号
    is_co, cp = is_controllable(param)

    if len(nodes) != 0 and is_co == -1:
        node = nodes[len(nodes) - 1]

        if isinstance(node, php.Assignment):  # 回溯的过程中，对出现赋值情况的节点进行跟踪
            param_node = get_node_name(node.node)  # param_node为被赋值的变量
            param_expr, expr_lineno, is_re = get_expr_name(node.expr)  # param_expr为赋值表达式,param_expr为变量或者列表

            if param == param_node and is_re is True:
                is_co = 0
                cp = None
                return is_co, cp, expr_lineno

            if param == param_node and not isinstance(param_expr, list):  # 找到变量的来源，开始继续分析变量的赋值表达式是否可控
                is_co, cp = is_controllable(param_expr)  # 开始判断变量是否可控

                if is_co != 1:
                    is_co, cp = is_sink_function(param_expr, function_params)

                param = param_expr  # 每次找到一个污点的来源时，开始跟踪新污点，覆盖旧污点

            if param == param_node and isinstance(param_expr, list):
                for expr in param_expr:
                    param = expr
                    is_co, cp = is_controllable(expr)

                    if is_co == 1:
                        return is_co, cp, expr_lineno

                    _is_co, _cp, expr_lineno = parameters_back(param, nodes[:-1], function_params)

                    if _is_co != -1:  # 当参数可控时，值赋给is_co 和 cp，有一个参数可控，则认定这个函数可能可控
                        is_co = _is_co
                        cp = _cp

        if is_co == -1:  # 当is_co为True时找到可控，停止递归
            is_co, cp, expr_lineno = parameters_back(param, nodes[:-1], function_params)  # 找到可控的输入时，停止递归

    elif len(nodes) == 0 and function_params is not None:
        for function_param in function_params:
            if function_param == param:
                is_co = 2
                cp = function_param

    return is_co, cp, expr_lineno


def get_function_params(nodes):
    """
    获取用户自定义函数的所有入参
    :param nodes: 自定义函数的参数部分
    :return: 以列表的形式返回所有的入参
    """
    params = []
    for node in nodes:

        if isinstance(node, php.FormalParameter):
            params.append(node.name)

    return params


def anlysis_function(node, back_node, vul_function, function_params, vul_lineno):
    """
    对用户自定义的函数进行分析-->获取函数入参-->入参用经过赋值流程，进入sink函数-->此自定义函数为危险函数
    :param node:
    :param back_node:
    :param vul_function:
    :param function_params:
    :param vul_lineno:
    :return:
    """
    global scan_results
    try:
        if node.name == vul_function and int(node.lineno) == int(vul_lineno):  # 函数体中存在敏感函数，开始对敏感函数前的代码进行检测
            for param in node.params:
                if isinstance(param.node, php.Variable):
                    analysis_variable_node(param.node, back_node, vul_function, vul_lineno, function_params)

                if isinstance(param.node, php.FunctionCall):
                    analysis_functioncall_node(param.node, back_node, vul_function, vul_lineno, function_params)

                if isinstance(param.node, php.BinaryOp):
                    analysis_binaryop_node(param.node, back_node, vul_function, vul_lineno, function_params)

                if isinstance(param.node, php.ArrayOffset):
                    analysis_arrayoffset_node(param.node, vul_function, vul_lineno)

    except Exception as e:
        logger.debug(e)


# def analysis_functioncall(node, back_node, vul_function, vul_lineno):
#     """
#     调用FunctionCall-->判断调用Function是否敏感-->get params获取所有参数-->开始递归判断
#     :param node:
#     :param back_node:
#     :param vul_function:
#     :param vul_lineno
#     :return:
#     """
#     global scan_results
#     try:
#         if node.name == vul_function and int(node.lineno) == int(vul_lineno):  # 定位到敏感函数
#             for param in node.params:
#                 if isinstance(param.node, php.Variable):
#                     analysis_variable_node(param.node, back_node, vul_function, vul_lineno)
#
#                 if isinstance(param.node, php.FunctionCall):
#                     analysis_functioncall_node(param.node, back_node, vul_function, vul_lineno)
#
#                 if isinstance(param.node, php.BinaryOp):
#                     analysis_binaryop_node(param.node, back_node, vul_function, vul_lineno)
#
#                 if isinstance(param.node, php.ArrayOffset):
#                     analysis_arrayoffset_node(param.node, vul_function, vul_lineno)
#
#     except Exception as e:
#         logger.debug(e)


def analysis_binaryop_node(node, back_node, vul_function, vul_lineno, function_params=None):
    """
    处理BinaryOp类型节点-->取出参数-->回溯判断参数是否可控-->输出结果
    :param node:
    :param back_node:
    :param vul_function:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    logger.debug('[AST] vul_function:{v}'.format(v=vul_function))
    params = get_binaryop_params(node)
    params = export_list(params, export_params=[])

    for param in params:
        is_co, cp, expr_lineno = parameters_back(param, back_node, function_params)
        set_scan_results(is_co, cp, expr_lineno, vul_function, param, vul_lineno)


def analysis_arrayoffset_node(node, vul_function, vul_lineno):
    """
    处理ArrayOffset类型节点-->取出参数-->回溯判断参数是否可控-->输出结果
    :param node:
    :param vul_function:
    :param vul_lineno:
    :return:
    """
    logger.debug('[AST] vul_function:{v}'.format(v=vul_function))
    param = get_node_name(node.node)
    expr_lineno = node.lineno
    is_co, cp = is_controllable(param)

    set_scan_results(is_co, cp, expr_lineno, vul_function, param, vul_lineno)


def analysis_functioncall_node(node, back_node, vul_function, vul_lineno, function_params=None):
    """
    处理FunctionCall类型节点-->取出参数-->回溯判断参数是否可控-->输出结果
    :param node:
    :param back_node:
    :param vul_function:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    logger.debug('[AST] vul_function:{v}'.format(v=vul_function))
    params = get_all_params(node.params)
    for param in params:
        is_co, cp, expr_lineno = parameters_back(param, back_node, function_params)
        set_scan_results(is_co, cp, expr_lineno, vul_function, param, vul_lineno)


def analysis_variable_node(node, back_node, vul_function, vul_lineno, function_params=None):
    """
    处理Variable类型节点-->取出参数-->回溯判断参数是否可控-->输出结果
    :param node:
    :param back_node:
    :param vul_function:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    logger.debug('[AST] vul_function:{v}'.format(v=vul_function))
    params = get_node_name(node)
    is_co, cp, expr_lineno = parameters_back(params, back_node, function_params)
    set_scan_results(is_co, cp, expr_lineno, vul_function, params, vul_lineno)


def analysis_if_else(node, back_node, vul_function, vul_lineno, function_params=None):
    nodes = []
    if isinstance(node.node, php.Block):  # if语句中的sink点以及变量
        analysis(node.node.nodes, vul_function, back_node, vul_lineno, function_params)

    if node.else_ is not None:  # else语句中的sink点以及变量
        if isinstance(node.else_.node, php.Block):
            analysis(node.else_.node.nodes, vul_function, back_node, vul_lineno, function_params)

    if len(node.elseifs) != 0:  # elseif语句中的sink点以及变量
        for i_node in node.elseifs:
            if i_node.node is not None:
                if isinstance(i_node.node, php.Block):
                    analysis(i_node.node.nodes, vul_function, back_node, vul_lineno, function_params)

                else:
                    nodes.append(i_node.node)
                    analysis(nodes, vul_function, back_node, vul_lineno, function_params)


def analysis_echo_print(node, back_node, vul_function, vul_lineno, function_params=None):
    """
    处理echo/print类型节点-->判断节点类型-->不同If分支回溯判断参数是否可控-->输出结果
    :param node:
    :param back_node:
    :param vul_function:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    global scan_results

    if int(vul_lineno) == int(node.lineno):
        if isinstance(node, php.Print):
            if isinstance(node.node, php.FunctionCall):
                analysis_functioncall_node(node.node, back_node, vul_function, vul_lineno, function_params)

            if isinstance(node.node, php.Variable) and vul_function == 'print':  # 直接输出变量信息
                analysis_variable_node(node.node, back_node, vul_function, vul_lineno, function_params)

            if isinstance(node.node, php.BinaryOp) and vul_function == 'print':
                analysis_binaryop_node(node.node, back_node, vul_function, vul_lineno, function_params)

            if isinstance(node.node, php.ArrayOffset) and vul_function == 'print':
                analysis_arrayoffset_node(node.node, vul_function, vul_lineno)

        elif isinstance(node, php.Echo):
            for k_node in node.nodes:
                if isinstance(k_node, php.FunctionCall):  # 判断节点中是否有函数调用节点
                    analysis_functioncall_node(k_node, back_node, vul_function, vul_lineno, function_params)  # 将含有函数调用的节点进行分析

                if isinstance(k_node, php.Variable) and vul_function == 'echo':
                    analysis_variable_node(k_node, back_node, vul_function, vul_lineno), function_params

                if isinstance(k_node, php.BinaryOp) and vul_function == 'echo':
                    analysis_binaryop_node(k_node, back_node, vul_function, vul_lineno, function_params)

                if isinstance(k_node, php.ArrayOffset) and vul_function == 'echo':
                    analysis_arrayoffset_node(k_node, vul_function, vul_lineno)


def analysis_eval(node, vul_function, back_node, vul_lineno, function_params=None):
    """
    处理eval类型节点-->判断节点类型-->不同If分支回溯判断参数是否可控-->输出结果
    :param node:
    :param vul_function:
    :param back_node:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    global scan_results

    if vul_function == 'eval' and int(node.lineno) == int(vul_lineno):
        if isinstance(node.expr, php.Variable):
            analysis_variable_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.FunctionCall):
            analysis_functioncall_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.BinaryOp):
            analysis_binaryop_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.ArrayOffset):
            analysis_arrayoffset_node(node.expr, vul_function, vul_lineno)


def analysis_file_inclusion(node, vul_function, back_node, vul_lineno, function_params=None):
    """
    处理include/require类型节点-->判断节点类型-->不同If分支回溯判断参数是否可控-->输出结果
    :param node:
    :param vul_function:
    :param back_node:
    :param vul_lineno:
    :param function_params:
    :return:
    """
    global scan_results
    include_fs = ['include', 'include_once', 'require', 'require_once']

    if vul_function in include_fs and int(node.lineno) == int(vul_lineno):
        logger.debug('[AST-INCLUDE] {l}-->{r}'.format(l=vul_function, r=vul_lineno))

        if isinstance(node.expr, php.Variable):
            analysis_variable_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.FunctionCall):
            analysis_functioncall_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.BinaryOp):
            analysis_binaryop_node(node.expr, back_node, vul_function, vul_lineno, function_params)

        if isinstance(node.expr, php.ArrayOffset):
            analysis_arrayoffset_node(node.expr, vul_function, vul_lineno)


def set_scan_results(is_co, cp, expr_lineno, sink, param, vul_lineno):
    """
    获取结果信息-->输出结果
    :param is_co:
    :param cp:
    :param expr_lineno:
    :param sink:
    :param param:
    :param vul_lineno:
    :return:
    """
    results = []
    global scan_results

    result = {
        'code': is_co,
        'source': cp,
        'source_lineno': expr_lineno,
        'sink': sink,
        'sink_param:': param,
        'sink_lineno': vul_lineno
    }
    if result['code'] != -1:  # 查出来漏洞结果添加到结果信息中
        results.append(result)
        scan_results += results


def analysis(nodes, vul_function, back_node, vul_lineo, function_params=None):
    """
    调用FunctionCall-->analysis_functioncall分析调用函数是否敏感
    :param nodes: 所有节点
    :param vul_function: 要判断的敏感函数名
    :param back_node: 各种语法结构里面的语句
    :param vul_lineo: 漏洞函数所在行号
    :param function_params: 自定义函数的所有参数列表
    :return:
    """
    buffer_ = []
    for node in nodes:
        if isinstance(node, php.FunctionCall):  # 函数直接调用，不进行赋值
            anlysis_function(node, back_node, vul_function, function_params, vul_lineo)

        elif isinstance(node, php.Assignment):  # 函数调用在赋值表达式中
            if isinstance(node.expr, php.FunctionCall):
                anlysis_function(node.expr, back_node, vul_function, function_params, vul_lineo)

            if isinstance(node.expr, php.Eval):
                analysis_eval(node.expr, vul_function, back_node, vul_lineo, function_params)

            if isinstance(node.expr, php.Silence):
                buffer_.append(node.expr)
                analysis(buffer_, vul_function, back_node, vul_lineo, function_params)

        elif isinstance(node, php.Print) or isinstance(node, php.Echo):
            analysis_echo_print(node, back_node, vul_function, vul_lineo, function_params)

        elif isinstance(node, php.Silence):
            nodes = get_silence_params(node)
            analysis(nodes, vul_function, back_node, vul_lineo)

        elif isinstance(node, php.Eval):
            analysis_eval(node, vul_function, back_node, vul_lineo, function_params)

        elif isinstance(node, php.Include) or isinstance(node, php.Require):
            analysis_file_inclusion(node, vul_function, back_node, vul_lineo, function_params)

        elif isinstance(node, php.If):  # 函数调用在if-else语句中时
            analysis_if_else(node, back_node, vul_function, vul_lineo, function_params)

        elif isinstance(node, php.While) or isinstance(node, php.For):  # 函数调用在循环中
            if isinstance(node.node, php.Block):
                analysis(node.node.nodes, vul_function, back_node, vul_lineo, function_params)

        elif isinstance(node, php.Function) or isinstance(node, php.Method):
            function_body = []
            function_params = get_function_params(node.params)
            analysis(node.nodes, vul_function, function_body, vul_lineo, function_params=function_params)

        elif isinstance(node, php.Class):
            analysis(node.nodes, vul_function, back_node, vul_lineo, function_params)

        back_node.append(node)


def scan_parser(code_content, sensitive_func, vul_lineno, repair):
    """
    开始检测函数
    :param code_content: 要检测的文件内容
    :param sensitive_func: 要检测的敏感函数,传入的为函数列表
    :param vul_lineno: 漏洞函数所在行号
    :param repair: 对应漏洞的修复函数列表
    :return:
    """
    try:
        global repairs
        global scan_results
        repairs = repair
        scan_results = []
        parser = make_parser()
        all_nodes = parser.parse(code_content, debug=False, lexer=lexer.clone(), tracking=with_line)
        for func in sensitive_func:  # 循环判断代码中是否存在敏感函数，若存在，递归判断参数是否可控;对文件内容循环判断多次
            back_node = []
            analysis(all_nodes, func, back_node, int(vul_lineno), function_params=None)
    except SyntaxError as e:
        logger.warning('[AST] [ERROR]:{e}'.format(e=e))

    return scan_results
