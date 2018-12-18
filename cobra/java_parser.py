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

import sys
import javalang

from javalang.tree import *
from cobra.log import logger
from cobra.rule import Rule

sys.setrecursionlimit(2000)


class JavaAst(object):
    def __init__(self, target_directory):
        self.target_directory = target_directory

        self.scan_results = []
        self.sources = []
        self.import_package = []
        self.class_path = []

        self.package_name = ''
        self.class_name = ''
        self.method_name = ''  # 用于正在存放正在回溯的方法名

        r = Rule()
        self.sources = r.sources

    # ####################### 分析语法结构 #############################
    def analysis(self, nodes, sink, back_node, vul_lineno, method_params=None):
        """
        解析语法结构，获取语法树内容，含有sink函数的语法由单独模块进行分析
        :param nodes: 语法树
        :param sink: 敏感函数
        :param back_node: 回溯节点
        :param vul_lineno: Sink函数所在行号
        :param method_params: 自定义函数的参数
        :return:
        """
        for path, node in nodes:
            try:
                if isinstance(node, CompilationUnit):
                    pass

                elif isinstance(node, PackageDeclaration):
                    self.package_name = node.name  # 获取package名

                elif isinstance(node, ClassDeclaration):
                    self.class_name = node.name  # 获取Class名

                elif isinstance(node, FormalParameter):
                    pass

                elif isinstance(node, ReferenceType):
                    pass

                elif isinstance(node, Import):
                    self.analysis_import(node)

                elif isinstance(node, StatementExpression):
                    self.analysis_nodes(node, sink, back_node, vul_lineno)

                elif isinstance(node, LocalVariableDeclaration):
                    self.analysis_nodes(node, sink, back_node, vul_lineno)

                elif isinstance(node, Literal):
                    pass

                elif isinstance(node, ReturnStatement):
                    self.analysis_nodes(node, sink, back_node, vul_lineno)

            except Exception as e:
                logger.debug('[Java-AST] [EXCEPTION] {e}'.format(e=e.message))

            back_node.append(node)

    def analysis_nodes(self, node, sink, back_node, vul_lineno):
        """
        用于定位不同语法类型的Sink函数位置，并进行参数的提取操作
        :param node:
        :param sink:
        :param back_node:
        :param vul_lineno:
        :param method_params:
        :return:
        """
        sink_list = sink.split(':')  # ['方法名', '包名']

        if len(sink_list) == 2:
            if isinstance(node, StatementExpression) or isinstance(node, ReturnStatement):
                node_line = self.get_node_lineno(node)
                if self.analysis_sink(node.expression, sink_list, vul_lineno, node_line):  # 判断是否为Sink函数
                    params = self.analysis_node(node.expression)  # 提取Sink函数的所有参数
                    logger.debug('[Java-AST] [SINK] Sink function param(s): {0}'.format(params))
                    self.start_analysis_params(params, sink, back_node)  # 开始回溯参数的来源

            if isinstance(node, LocalVariableDeclaration):
                node_line = self.get_node_lineno(node)
                if self.analysis_sink(node.declarators, sink_list, vul_lineno, node_line):
                    params = self.analysis_node(node)
                    logger.debug('[Java-AST] [SINK] Sink function param(s): {0}'.format(params))
                    self.start_analysis_params(params, sink, back_node)

        else:
            logger.warning('[Java-AST] The sink function list index out of range')

    def analysis_sink(self, node, sink, vul_lineno, node_line):
        """
        用于判断node节点中是否存在Sink函数
        :param node:
        :param sink:
        :param vul_lineno: Sink函数行号
        :param node_line: 当前节点行号
        :return:
        """
        if isinstance(node, MethodInvocation):
            result = self.analysis_sink_method_invocation(node, sink, vul_lineno)
            return result

        if isinstance(node, ClassCreator):
            result = self.analysis_sink_method_invocation(node.type, sink, vul_lineno, node_line)
            return result

        if isinstance(node, BinaryOperation):
            result = self.analysis_sink_method_invocation(node, sink, vul_lineno, node_line)
            return result

        if isinstance(node, Assignment):  # 分析StatementExpression语法
            if isinstance(node.value, MethodInvocation):
                result = self.analysis_sink_method_invocation(node.value, sink, vul_lineno)
                return result

            if isinstance(node.value, ClassCreator):
                result = self.analysis_sink_method_invocation(node.value.type, sink, vul_lineno, node_line)
                return result

            if isinstance(node.value, BinaryOperation):
                result = self.analysis_sink_method_invocation(node.value, sink, vul_lineno, node_line)
                return result

        if isinstance(node, list):  # 分析LocalVariableDeclaration语法
            for n in node:
                if isinstance(n, VariableDeclarator):
                    if isinstance(n.initializer, MethodInvocation) or isinstance(n.initializer, ClassCreator):
                        result = self.analysis_sink(n.initializer, sink, vul_lineno, node_line)
                        return result

                    if isinstance(n.initializer, BinaryOperation):
                        result = self.analysis_sink(n.initializer, sink, vul_lineno, node_line)
                        return result

        return False

    def analysis_sink_method_invocation(self, node, sink, vul_lineno, node_line=0):
        """
        判断Sink函数是否存在 --> MethodInvocation
        :param node:
        :param sink: list, [方法名，包名]
        :param vul_lineno:
        :param node_line:
        :return:
        """
        if isinstance(node, MethodInvocation):
            qualifier = node.qualifier  # 对象名
            member = node.member  # 方法名
        elif isinstance(node, ReferenceType):
            member = node.name
        elif isinstance(node, BinaryOperation):
            member = self.get_deep_binary_operation_params(node, code=2)
        else:
            member = None

        if node_line == 0:
            lineno = self.get_node_lineno(node)
        else:
            lineno = node_line

        if isinstance(member, list):
            for m in member:
                result = self.analysis_sink_member(sink, vul_lineno, lineno, m)
                if result is True:
                    return result

        else:
            result = self.analysis_sink_member(sink, vul_lineno, lineno, member)
            if result is True:
                return result

        return False

    def analysis_sink_member(self, sink, vul_lineno, lineno, member):
        """
        判断member是否为Sink
        :param sink:
        :param vul_lineno:
        :param lineno:
        :param member:
        :return:
        """
        if sink[1] != '':  # 包名不为空
            # Sink所在文件检测，包名未被import，根据package和class判断
            if sink[1].strip() == (self.package_name + '.' + self.class_name).strip():
                if int(lineno) == int(vul_lineno) and sink[0] == member:
                    logger.debug('[Java-AST] Found the sink function --> {q} in line {l}'.format(q=sink[0], l=lineno))
                    return True

            # Sink所在文件外检测，包名直接被import，根据import的类进行判断
            else:
                if int(lineno) == int(vul_lineno) and sink[0] == member and sink[1] in self.import_package:  # 判断方法是否为Sink点
                    logger.debug('[Java-AST] Found the sink function --> {q}:{m} in line {l}'.format(q=sink[0], m=sink[1], l=lineno))
                    return True

        elif sink[1] == '':  # 包名为空
            if int(lineno) == int(vul_lineno) and sink[0] == member:
                logger.debug('[Java-AST] Found the sink function --> {q} in line {l}'.format(q=sink[0], l=lineno))
                return True

        else:
            return False

    # ####################### 回溯参数传递 #############################
    def start_analysis_params(self, params, sink, back_node):
        """
        用于开始对Sink函数的参数进行回溯，并收集记录回溯结果
        :param params:
        :param sink:
        :param back_node:
        :return:
        """
        try:
            if isinstance(params, list):
                for param in params:
                    logger.debug('[Java-AST] [SINK] Start back param --> {0}'.format(param))
                    is_controllable = self.back_statement_expression(param, back_node)
                    self.set_scan_results(is_controllable, sink)

            else:
                logger.debug('[Java-AST] [SINK] Start back param --> {0}'.format(params))
                is_controllable = self.back_statement_expression(params, back_node)
                self.set_scan_results(is_controllable, sink)
        except RuntimeError:
            logger.debug('Maximum recursion depth exceeded')

    def back_statement_expression(self, param, back_node):
        """
        开始回溯Sink函数参数
        :param param:
        :param back_node:
        :return:
        """
        # is_controllable = self.is_controllable(param)
        is_controllable = -1

        if len(back_node) != 0 and is_controllable == -1:
            node = back_node[len(back_node)-1]
            lineno = self.get_node_lineno(node)

            if isinstance(node, LocalVariableDeclaration):
                node_param = self.get_node_name(node.declarators)  # 获取被赋值变量
                expr_param, sink = self.get_expr_name(node.declarators)  # 取出赋值表达式中的内容

                is_controllable = self.back_node_is_controllable(node_param, param, sink, expr_param, lineno,
                                                                 back_node)

            if isinstance(node, Assignment):
                node_param = self.get_node_name(node.expressionl)
                expr_param, sink = self.get_expr_name(node.value)  # expr_param为方法名, sink为回溯变量

                is_controllable = self.back_node_is_controllable(node_param, param, sink, expr_param, lineno,
                                                                 back_node)

            if isinstance(node, FormalParameter):
                node_param = self.get_node_name(node)  # 获取被赋值变量
                expr_param, sink = self.get_expr_name(node)  # 取出赋值表达式中的内容

                is_controllable = self.back_node_is_controllable(node_param, param, sink, expr_param, lineno,
                                                                 back_node)

            if isinstance(node, StatementExpression):
                if isinstance(node.expression, Assignment):
                    node_param = self.get_node_name(node.expression.expressionl)
                    expr_param, sink = self.get_expr_name(node.expression.value)
                    is_controllable = self.back_node_is_controllable(node_param, param, sink, expr_param, lineno,
                                                                     back_node)

            if isinstance(node, MethodDeclaration):
                self.method_name = node.name
                method_params = self.get_method_declaration(node)
                is_controllable = self.is_sink_method(param, method_params)

                if is_controllable == 4:  # 参数来自于自定义函数，判断是否为Spring框架的HTTP入参
                    annotations = self.get_annotations_name(node.annotations)
                    for annotation in annotations:
                        if annotation == 'RequestMapping':
                            is_controllable = 1
                            return is_controllable

                if is_controllable == -1:  # 以方法定义为界限，回溯到一个方法体结束仍然没有结果，则直接返回结果，漏洞不存在
                    return is_controllable

            if is_controllable == -1:
                is_controllable = self.back_statement_expression(param, back_node[:-1])

        # elif len(back_node) == 0 and is_controllable == -1:
        #     is_controllable = self.is_sink_method(param, method_params)

        return is_controllable

    def back_node_is_controllable(self, node_param, param, sink, expr_param, lineno, back_node):
        """
        对回溯的节点进行可控判断，并对多参数的
        :param node_param:
        :param param:
        :param sink:
        :param expr_param:
        :param lineno:
        :param back_node:
        :return:
        """
        is_controllable = -1

        if node_param == param and not isinstance(sink, list) and is_controllable == -1:
            logger.debug('[Java-AST] [BACK] analysis sink  {s} --> {t} in line {l}'.format(s=param, t=sink,
                                                                                           l=lineno))
            param = sink
            is_controllable = self.is_controllable(expr_param, lineno)

        if node_param == param and isinstance(sink, list) and is_controllable == -1:
            is_controllable = self.is_controllable(expr_param, lineno)

            for s in sink:
                param = s
                if is_controllable != -1:
                    return is_controllable

                logger.debug('[Java-AST] [BACK] analysis sink  {s} --> {t} in line {l}'.format(s=param, t=s,
                                                                                               l=lineno))
                _is_controllable = self.back_statement_expression(param, back_node[:-1])

                if _is_controllable != -1:
                    is_controllable = _is_controllable

        return is_controllable

    # ####################### 分析节点类型 #############################
    def analysis_node(self, node):
        """
        获取Sink函数参数
        :param node:
        :return:
        """
        if isinstance(node, MethodInvocation):
            param = self.get_node_arguments(node.arguments)
            return param

        elif isinstance(node, LocalVariableDeclaration):
            param = self.analysis_variable_declaration(node.declarators)
            return param

        elif isinstance(node, Assignment):
            param = self.analysis_assignment(node.value)
            return param

        else:
            logger.debug("[Java-AST] Can't analysis node --> {n} in analysis_node method".format(n=node))
            return ''

    def analysis_variable_declaration(self, nodes):
        for node in nodes:
            if isinstance(node, VariableDeclarator):
                if isinstance(node.initializer, MethodInvocation) or isinstance(node.initializer, ClassCreator):
                    params = self.get_method_invocation_params(node.initializer)
                    return params

                if isinstance(node.initializer, BinaryOperation):
                    params = self.get_binary_operation_params(node.initializer)
                    return params

    def analysis_assignment(self, node):
        if isinstance(node, MethodInvocation) or isinstance(node, ClassCreator):
            param = self.get_method_invocation_params(node)
            return param

        if isinstance(node, BinaryOperation):
            param = self.get_binary_operation_params(node)
            return param

        else:
            logger.debug("[Java-AST] Can't analysis node --> {n} in analysis_assignment method".format(n=node))

    def analysis_import(self, node):
        if hasattr(node, 'path'):
            self.import_package.append(node.path)

    def analysis_method_declaration(self, node, sink, vul_lineno):
        """
        获取自定义方法入参，由analysis分析自定义方法是否为敏感方法，用于之后的多级方法调用检测
        :param node:
        :param sink:
        :param vul_lineno:
        :return:
        """
        method_body = []
        nodes = []
        method_params = self.get_method_declaration(node)
        self.method_name = node.name
        if node.body is not None:
            for n in node.body:  # analysis分析节点为元组类型，整理数据结构
                body = ('', n)
                nodes.append(body)

        self.analysis(nodes, sink, method_body, vul_lineno, method_params)

    # ####################### 提取参数内容 #############################
    @staticmethod
    def get_method_declaration(nodes):
        """
        用于获取自定义方法体的参数
        :param nodes:
        :return:
        """
        params = []

        for node in nodes.parameters:
            if isinstance(node, FormalParameter):
                params.append(node.name)

        return params

    def get_node_arguments(self, nodes):
        """
        用于获取node.arguments中的所有参数
        :param nodes:
        :return: list
        """
        params_list = []
        for node in nodes:
            if isinstance(node, MemberReference):
                param = self.get_member_reference_name(node)
                params_list.append(param)

            if isinstance(node, BinaryOperation):
                params = self.get_binary_operation_params(node)
                params_list.append(params)

            if isinstance(node, MethodInvocation) or isinstance(node, ClassCreator):
                params = self.get_method_invocation_params(node)
                params_list.append(params)

        return self.export_list(params_list, [])

    def get_method_invocation_params(self, node):
        """
        获取MethodInvocation和ClassCreator两种语法类型的参数
        :param node:
        :return:
        """
        params_list = []
        qualifier = self.get_method_object_name(node)
        if qualifier is not '' and qualifier is not None:
            params_list.append(qualifier)

        for argument in node.arguments:
            if isinstance(argument, MethodInvocation) or isinstance(argument, ClassCreator):
                params = self.get_method_invocation_params(argument)
                params_list.append(params)

            else:
                if isinstance(argument, MemberReference):
                    params = self.get_member_reference_name(argument)
                    params_list.append(params)

                if isinstance(argument, BinaryOperation):
                    params = self.get_binary_operation_params(argument)
                    params_list.append(params)

                if isinstance(argument, Literal):
                    params = self.get_literal_params(argument)
                    params_list.append(params)

        return self.export_list(params_list, [])

    def get_method_invocation_member(self, node):
        """
        取方法调用的 对象名 + 方法名
        :param node:
        :return:
        """
        qualifier = node.qualifier
        member = node.member
        # result = qualifier + '.' + member
        result = member
        lineno = self.get_node_lineno(node)
        logger.debug('[Java-AST] analysis method --> {r} in line {l}'.format(r=result, l=lineno))
        return result

    @staticmethod
    def get_class_creator_type(node):
        """
        用于获取ClassCreator类型的type类型，类名
        :param node:
        :return:
        """
        if isinstance(node, ReferenceType):
            return node.name

        else:
            return ''

    def get_binary_operation_params(self, node, code=1):  # 当为BinaryOp类型时，分别对left和right进行处理，取出需要的变量
        """

        :param node:
        :param code: code==1取BinaryOp中的参数，code==2时取方法名，默认为1
        :return:
        """
        params = []

        if isinstance(node.operandr, MemberReference) or isinstance(node.operandl, MemberReference):
            if isinstance(node.operandr, MemberReference):
                param = self.get_member_reference_name(node.operandr)
                params.append(param)

            if isinstance(node.operandl, MemberReference):
                param = self.get_member_reference_name(node.operandl)
                params.append(param)

        if not isinstance(node.operandr, MemberReference) or not isinstance(node.operandl, MemberReference):
            param_right = self.get_deep_binary_operation_params(node.operandr, code)
            param_left = self.get_deep_binary_operation_params(node.operandl, code)

            if code == 1:
                params = list(param_right) + list(param_left) + list(params)
            else:
                params = [param_right, param_left, params]

        params = self.export_list(params, [])
        return params

    def get_deep_binary_operation_params(self, node, code=1):
        param = []

        if isinstance(node, BinaryOperation):
            param = self.get_binary_operation_params(node, code)

        if (isinstance(node, MethodInvocation) or isinstance(node, ClassCreator)) and code == 1:
            param = self.get_method_invocation_params(node)

        if (isinstance(node, MethodInvocation) or isinstance(node, ClassCreator)) and code == 2:
            param = self.get_method_invocation_member(node)

        return param

    def get_annotations_name(self, nodes):
        """
        提取Spring框架中annotations的类型
        :param nodes:
        :return:
        """
        annotations = []
        if isinstance(nodes, list):
            for node in nodes:
                if isinstance(node, Annotation):
                    annotations.append(node.name)

        return annotations

    def get_method_object_name(self, node):
        """
        提取调用方法的实例化对象的变量名
        :param node:
        :return:
        """
        return node.qualifier

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

            if isinstance(nodes, FormalParameter):  # 取出Spring框架注解的入参
                param_node = nodes.name

        except IndexError as e:
            logger.warning(e.message)

        return param_node

    def get_expr_name(self, nodes):
        """
        用来获取表达式节点信息
        :param node:
        :return:  expr_node(用于判断是否可控)，sink(用于跟踪参数传递)
        """
        expr_param = ''
        sink = ''

        if isinstance(nodes, MethodInvocation):  # 当赋值表达式为方法调用
            sink = self.get_method_invocation_params(nodes)
            expr_param = self.get_method_invocation_member(nodes)
            return expr_param, sink

        if isinstance(nodes, ClassCreator):
            sink = self.get_node_arguments(nodes.arguments)
            expr_param = self.get_class_creator_type(nodes.type)
            return expr_param, sink

        elif isinstance(nodes, FormalParameter):  # 取出Spring框架注解类型 和 参数
            sink = nodes.name
            expr_param = self.get_annotations_name(nodes.annotations)
            return expr_param, sink

        if isinstance(nodes, BinaryOperation):
            sink = self.get_binary_operation_params(nodes)
            expr_param = self.get_deep_binary_operation_params(nodes, code=2)
            return expr_param, sink

        elif isinstance(nodes, list):
            for node in nodes:
                if isinstance(node.initializer, MethodInvocation):
                    sink = self.get_method_invocation_params(node.initializer)
                    expr_param = self.get_method_invocation_member(node.initializer)
                    return expr_param, sink

                if isinstance(node.initializer, ClassCreator):
                    sink = self.get_node_arguments(node.initializer.arguments)
                    expr_param = self.get_class_creator_type(node.initializer.type)
                    return expr_param, sink

                if isinstance(node.initializer, BinaryOperation):
                    sink = self.get_binary_operation_params(node.initializer)
                    expr_param = self.get_deep_binary_operation_params(node, code=2)
                    return expr_param, sink

                else:
                    logger.debug("Can't analysis node --> {} in get_expr_name method".format(node))
                    return expr_param, sink

        else:
            logger.debug("Can't analysis node --> {} in get_expr_name method".format(nodes))
            return expr_param, sink

    def get_node_lineno(self, node):
        lineno = 0

        if hasattr(node, '_position'):
            lineno = node._position[0]

        elif isinstance(node, Assignment):
            if isinstance(node.value, MethodInvocation):
                lineno = node.value._position[0]

            if isinstance(node.expressionl, MemberReference):
                lineno = node.expressionl._position[0]

        elif isinstance(node, StatementExpression):
            lineno = self.get_node_lineno(node.expression)

        elif isinstance(node, VariableDeclarator):
            lineno = self.get_node_lineno(node.initializer)

        return lineno

    # ####################### 分析语法结构 #############################
    def is_controllable(self, expr, lineno=0):
        """
        用于判断是否调用了外部传参
        :param expr:
        :param lineno:
        :return:
        """
        if isinstance(expr, list):
            for e in expr:
                for key in self.sources:
                    if str(e) in self.sources[key]:
                        if key in self.import_package:
                            logger.debug('[Java-AST] Found the source function --> {e} in line {l}'.format(e=e,
                                                                                                           l=lineno))
                            return 1
        else:
            for key in self.sources:
                if str(expr) in self.sources[key]:
                    if key in self.import_package:
                        logger.debug('[Java-AST] Found the source function --> {e} in line {l}'.format(e=expr,
                                                                                                       l=lineno))
                        return 1
        return -1

    @staticmethod
    def is_sink_method(sinks, method_params):
        is_controllable = -1

        if isinstance(sinks, list) and method_params is not None:
            for sink in sinks:
                for method_param in method_params:
                    if sink == method_param:
                        is_controllable = 4
                        logger.debug('[Java-AST] [METHOD] Found the user sink function --> {e}'.format(e=sink))

        if not isinstance(sinks, list) and method_params is not None:
            for method_param in method_params:
                if sinks == method_param:
                    is_controllable = 4
                    logger.debug('[Java-AST] [METHOD] Found the user sink function --> {e}'.format(e=sinks))

        return is_controllable

    # ####################### 保存扫描结果 #############################
    def set_scan_results(self, is_controllable, sink):
        """
        用于获取扫描结果
        :param is_controllable:
        :param sink:
        :return:
        """
        if self.package_name != '' and self.class_name != '':
            u_sink = self.method_name + ':' + self.package_name + '.' + self.class_name

        else:
            u_sink = self.method_name + ':'

        if is_controllable == 1:
            result = {
                'code': is_controllable,
                'sink': sink
            }

        elif is_controllable == 4:
            if sink == u_sink:
                is_controllable = -1
                logger.debug('[Java-AST] Sink is u_sink, exit analysis...')
            else:
                is_controllable = 4

            result = {
                'code': is_controllable,
                'sink': sink,
                'u_sink': u_sink
            }

        else:
            result = {
                'code': -1,
                'sink': ''
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


def java_scan_parser(code_content, sensitive_func, vul_lineno, target_directory):
    back_node = []
    tree = javalang.parse.parse(code_content)
    java_ast = JavaAst(target_directory)
    if isinstance(sensitive_func, list):
        for sink in sensitive_func:
            java_ast.analysis(tree, sink, back_node, vul_lineno)
    else:
        java_ast.analysis(tree, sensitive_func, back_node, vul_lineno)

    return java_ast.scan_results
