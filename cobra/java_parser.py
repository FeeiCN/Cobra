#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    Project
    ~~~~~

    Project ins

    :author:    BlBana <635373043@qq.com>
    :homepage:  http://drops.blbana.cc
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 BlBana. All rights reserved
"""

import javalang
import logging
from javalang.tree import *
from cobra.log import logger


class JavaAst(object):
    def __init__(self):
        self.scan_results = []

    # ####################### 分析语法结构 #############################
    def analysis(self, nodes, sink, back_node, vul_lineno):
        """
        解析语法结构，获取语法树内容，含有sink函数的语法由单独模块进行分析
        :param nodes: 语法树
        :param sink: 敏感函数
        :param back_node: 回溯节点
        :return:
        """
        for path, node in nodes:
            if isinstance(node, CompilationUnit):
                pass

            elif isinstance(node, ClassDeclaration):
                pass

            elif isinstance(node, MethodDeclaration):
                pass

            elif isinstance(node, FormalParameter):
                pass

            elif isinstance(node, ReferenceType):
                pass

            elif isinstance(node, StatementExpression):
                self.analysis_statement_expression(node, sink, back_node, vul_lineno)

            elif isinstance(node, LocalVariableDeclaration):
                self.analysis_local_variable_declaration(node, sink, back_node, vul_lineno)

            elif isinstance(node, MethodInvocation):
                pass

            elif isinstance(node, Literal):
                pass

            back_node.append(node)

    def analysis_statement_expression(self, node, sink, back_node, vul_lineno):
        """
        用于定位statementExpression类型结构的sink点
        :param node:
        :param sink:
        :param back_node:
        :return:
        """
        sink_list = sink.split('.')

        if len(sink_list) == 2:
            if self.analysis_sink(node.expression, sink_list, vul_lineno):
                params = self.analysis_node(node.expression)

                if isinstance(params, list):
                    for param in params:
                        is_controllable = self.back_statement_expression(param, back_node)
                        self.set_scan_results(is_controllable, sink)

                else:
                    is_controllable = self.back_statement_expression(params, back_node)
                    self.set_scan_results(is_controllable, sink)

        else:
            logger.warning('[Java-AST] The sink function list index out of range')

    def analysis_local_variable_declaration(self, node, sink, back_node, vul_lineno):
        sink_list = sink.split('.')

        if len(sink_list) == 2:
            if self.analysis_sink(node.declarators, sink_list, vul_lineno):
                params = self.analysis_node(node)

                if isinstance(params, list):
                    for param in params:
                        is_controllable = self.back_statement_expression(param, back_node)
                        self.set_scan_results(is_controllable, sink)

                else:
                    is_controllable = self.back_statement_expression(params, back_node)
                    self.set_scan_results(is_controllable, sink)

        else:
            logger.warning('[Java-AST] The sink function list index out of range')

    def analysis_sink(self, node, sink, vul_lineno):
        """
        用于判断node节点中是否存在Sink函数
        :param node:
        :param sink:
        :return:
        """
        if isinstance(node, MethodInvocation):
            result = self.analysis_sink_method_invocation(node, sink, vul_lineno)
            return result

        if isinstance(node, Assignment):
            if isinstance(node.value, MethodInvocation):
                result = self.analysis_sink_method_invocation(node.value, sink, vul_lineno)
                return result

        if isinstance(node, list):
            for n in node:
                if isinstance(n, VariableDeclarator):
                    if isinstance(n.initializer, MethodInvocation):
                        result = self.analysis_sink(n.initializer, sink, vul_lineno)
                        return result

        return False

    def analysis_sink_method_invocation(self, node, sink, vul_lineno):
        """
        判断Sink函数是否存在
        :param node:
        :param sink:
        :return:
        """
        qualifier = node.qualifier
        member = node.member
        lineno = self.get_node_lineno(node)

        if sink[0] == qualifier and sink[1] == member and int(lineno) == int(vul_lineno):  # 判断方法是否为Sink点
            logger.debug('[Java-AST] Found the sink function --> {q}.{m} in line {l}'.format(q=sink[0], m=sink[1], l=lineno))
            return True

        else:
            return False

    # ####################### 回溯参数传递 #############################
    def back_statement_expression(self, param, back_node):

        is_controllable = self.is_controllable(param)

        if len(back_node) != 0 and is_controllable == -1:
            node = back_node[len(back_node)-1]
            lineno = self.get_node_lineno(node)

            if isinstance(node, LocalVariableDeclaration):
                node_param = self.get_node_name(node.declarators)  # 获取被赋值变量
                expr_param, sink = self.get_expr_name(node.declarators)  # 取出赋值表达式中的内容

                if node_param == param and not isinstance(sink, list):
                    logger.debug('[Java-AST] analysis sink --> {s} in line {l}'.format(s=sink, l=lineno))
                    param = sink
                    is_controllable = self.is_controllable(expr_param, lineno)

                if node_param == param and isinstance(sink, list):
                    is_controllable = self.is_controllable(expr_param, lineno)

                    for s in sink:
                        logger.debug('[Java-AST] analysis sink --> {s} in line {l}'.format(s=s,
                                                                                           l=lineno))
                        param = s

                        if is_controllable == 1:
                            return is_controllable

                        _is_controllable = self.back_statement_expression(param, back_node[:-1])

                        if _is_controllable != -1:
                            is_controllable = _is_controllable

            if isinstance(node, Assignment):
                node_param = self.get_node_name(node.expressionl)
                expr_param, sink = self.get_expr_name(node.value)  # expr_param为方法名, sink为回溯变量

                if node_param == param and not isinstance(sink, list):
                    logger.debug('[Java-AST] analysis sink --> {s} in line {l}'.format(s=sink, l=lineno))
                    param = sink
                    is_controllable = self.is_controllable(expr_param, lineno)

                if node_param == param and isinstance(sink, list):
                    is_controllable = self.is_controllable(expr_param, lineno)

                    for s in sink:
                        logger.debug('[Java-AST] analysis sink --> {s} in line {l}'.format(s=s,
                                                                                           l=lineno))
                        param = s

                        if is_controllable == 1:
                            return is_controllable

                        _is_controllable = self.back_statement_expression(param, back_node[:-1])

                        if _is_controllable != -1:
                            is_controllable = _is_controllable

            if is_controllable == -1:
                is_controllable = self.back_statement_expression(param, back_node[:-1])

        return is_controllable

    # ####################### 提取参数内容 #############################
    def analysis_node(self, node):
        if isinstance(node, MethodInvocation):
            param = self.analysis_method_invocation(node.arguments)
            return param

        elif isinstance(node, LocalVariableDeclaration):
            param = self.analysis_variable_declaration(node.declarators)
            return param

        elif isinstance(node, Assignment):
            param = self.analysis_assignment(node.value)
            return param

        else:
            lineno = self.get_node_lineno(node)
            logger.warning("[Java-AST] Can't analysis node --> {n} in line {l}".format(n=node, l=lineno))
        # for declarator in node.declarators:
        #     if isinstance(declarator, VariableDeclarator):
        #         if isinstance(declarator.initializer, MethodInvocation):
        #             for argument in declarator.initializer.arguments:
        #                 if isinstance(argument, BinaryOperation):
        #                     if isinstance(argument.operandr, MemberReference):
        #                         param = self.get_member_reference_name(argument.operandr)
        #                         return param

    def analysis_method_invocation(self, nodes):
        for node in nodes:
            if isinstance(node, MemberReference):
                param = self.get_member_reference_name(node)
                return param

            if isinstance(node, BinaryOperation):
                params = self.get_binary_operation_params(node)
                return params

            if isinstance(node, MethodInvocation):
                params = self.get_method_invocation_params(node)
                return params

    def analysis_variable_declaration(self, nodes):
        for node in nodes:
            if isinstance(node, VariableDeclarator):
                if isinstance(node.initializer, MethodInvocation):
                    params = self.get_method_invocation_params(node.initializer)
                    return params

    def analysis_assignment(self, node):
        if isinstance(node, MethodInvocation):
            param = self.get_method_invocation_params(node)
            return param

        else:
            lineno = self.get_node_lineno(node)
            logger.warning("[Java-AST] Can't analysis node --> {n} in line {l}".format(n=node, l=lineno))

    def get_method_invocation_params(self, node):
        params = ''
        for argument in node.arguments:
            if isinstance(argument, MethodInvocation):
                params = self.get_method_invocation_params(argument)

            else:
                if isinstance(argument, MemberReference):
                    params = self.get_member_reference_name(argument)

                if isinstance(argument, BinaryOperation):
                    params = self.get_binary_operation_params(argument)

                if isinstance(argument, Literal):
                    params = self.get_literal_params(argument)

        return params

    def get_method_invocation_member(self, node):
        """
        取方法调用的 对象名 + 方法名
        :param node:
        :return:
        """
        qualifier = node.qualifier
        member = node.member
        result = qualifier + '.' + member
        lineno = self.get_node_lineno(node)
        logger.debug('[Java-AST] analysis method --> {r} in line {l}'.format(r=result, l=lineno))
        return result

    def get_binary_operation_params(self, node):  # 当为BinaryOp类型时，分别对left和right进行处理，取出需要的变量
        params = []

        if isinstance(node.operandr, MemberReference) or isinstance(node.operandl, MemberReference):
            if isinstance(node.operandr, MemberReference):
                param = self.get_member_reference_name(node.operandr)
                params.append(param)

            if isinstance(node.operandl, MemberReference):
                param = self.get_member_reference_name(node.operandl)
                params.append(param)

        if not isinstance(node.operandr, MemberReference) or not isinstance(node.operandl, MemberReference):
            param_right = self.get_deep_binary_operation_params(node.operandr)
            param_left = self.get_deep_binary_operation_params(node.operandl)

            params = param_right + param_left + params

        params = self.export_list(params, [])
        return params

    def get_deep_binary_operation_params(self, node):
        param = []

        if isinstance(node, BinaryOperation):
            param = self.get_binary_operation_params(node)

        if isinstance(node, MethodInvocation):
            param = self.get_method_invocation_params(node)

        return param

    def get_member_reference_name(self, node):
        """
        提取MemberReference语法中的参数
        :param node: MemberReference语法节点
        :return: 返回提取的参数变量
        """
        return node.member

    def get_literal_params(self, node):
        """
        取Literal常亮的值
        :param node:
        :return:
        """
        return node.value

    def get_node_name(self, nodes):
        """
        node回溯节点-->提取被复制变量名
        :param node:
        :return:
        """
        param_node = ''
        try:
            if isinstance(nodes, list):  # 取出LocalVariableDeclaration结构的变量名
                for node in nodes:
                    if isinstance(node, VariableDeclarator):
                        param_node = node.name

            if isinstance(nodes, MemberReference):  # 取出Assinment结构的变量名
                param_node = self.get_member_reference_name(nodes)

        except IndexError as e:
            logger.warning(e.message)

        return param_node

    def get_expr_name(self, nodes):
        """
        用来获取表达式节点信息
        :param node:
        :return:  expr_node(用于判断是否可控)，sink(用于跟踪参数传递)
        """
        if isinstance(nodes, MethodInvocation):  # 当赋值表达式为方法调用
            sink = self.get_method_invocation_params(nodes)
            expr_param = self.get_method_invocation_member(nodes)
            return expr_param, sink

        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node.initializer, MethodInvocation):
                    sink = self.get_method_invocation_params(node.initializer)
                    expr_param = self.get_method_invocation_member(node.initializer)
                    return expr_param, sink

    def get_node_lineno(self, node):
        lineno = 0

        if hasattr(node, '_position'):
            lineno = node._position[0]

        elif isinstance(node, Assignment):
            if isinstance(node.value, MethodInvocation):
                lineno = node.value._position[0]

        elif isinstance(node, StatementExpression):
            lineno = self.get_node_lineno(node.expression)

        elif isinstance(node, VariableDeclarator):
            lineno = self.get_node_lineno(node.initializer)

        return lineno

    # ####################### 分析语法结构 #############################
    def is_controllable(self, expr, lineno=0):
        controlled_params = [
            'request.getParameter'
        ]
        if str(expr) in controlled_params:
            logger.debug('[Java-AST] Found the source function --> {e} in line {l}'.format(e=expr,
                                                                                           l=lineno))
            return 1
        return -1

    # ####################### 保存扫描结果 #############################
    def set_scan_results(self, is_controllable, sink):
        result = {
            'code': is_controllable,
            'sink': sink
        }

        if result['code'] != -1:
            self.scan_results.append(result)

    # ####################### 保存扫描结果 #############################
    def export_list(self, params, export_params):
        """
        将params中嵌套的多个列表，导出为一个列表
        :param params:
        :param export_params:
        :return:
        """
        for param in params:
            if isinstance(param, list):
                export_params = self.export_list(param, export_params)

            else:
                export_params.append(param)

        return export_params

def java_scan_parser(code_content, sensitive_func, vul_lineno):
    back_node = []
    tree = javalang.parse.parse(code_content)
    java_ast = JavaAst()
    for sink in sensitive_func:
        java_ast.analysis(tree, sink, back_node, vul_lineno)
    return java_ast.scan_results
