# -*- coding: utf-8 -*-

"""
    templite
    ~~~~~~~~

    A simple template engine

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import re


class TempliteSyntaxError(ValueError):
    pass


class CodeBuilder(object):
    INDENT_STEP = 4

    def __init__(self, indent=0):
        self.code = []
        self.indent_level = indent

    def __str__(self):
        return "".join(str(c) for c in self.code)

    def add_line(self, line):
        """
        添加一行
        :param line:
        :return:
        """
        self.code.extend([" " * self.indent_level, line, "\n"])

    def add_section(self):
        """
        将模板里使用的变量赋值
        :return:
        """
        section = CodeBuilder(self.indent_level)
        self.code.append(section)
        return section

    def indent(self):
        """
        添加缩进
        :return:
        """
        self.indent_level += self.INDENT_STEP

    def dedent(self):
        """
        减小缩进
        :return:
        """
        self.indent_level -= self.INDENT_STEP

    def get_globals(self):
        """
        返回命名空间字典
        :return:
        """
        # 检查缩进，保证所有块都已处理完
        assert self.indent_level == 0
        # 得到 Python 代码
        python_source = str(self)
        # 执行代码，得到命名空间，返回
        global_namespace = {}
        exec (python_source, global_namespace)
        return global_namespace


class Templite(object):
    def __init__(self, text, *contexts):
        """
        :param text:输入的模板
        :param contexts:输入的数据和过滤器参数
        """
        self.context = {}
        for context in contexts:
            self.context.update(context)

        self.all_vars = set()
        self.loop_vars = set()

        # We construct a function in source form, then compile it and hold onto
        # it, and execute it to render the template.
        code = CodeBuilder()

        code.add_line("def render_function(context, do_dots):")
        code.indent()
        vars_code = code.add_section()
        code.add_line("result = []")
        code.add_line("append_result = result.append")
        code.add_line("extend_result = result.extend")
        code.add_line("to_str = str")

        buffered = []

        def flush_output():
            """
            简化向 code 添加代码的过程
            :return:
            """
            if len(buffered) == 1:
                code.add_line("append_result(%s)" % buffered[0])
            elif len(buffered) > 1:
                code.add_line("extend_result([{0}])".format(", ".join(buffered)))
            del buffered[:]

        # 利用一个栈保存操作符 for if 等
        ops_stack = []

        # 分割 HTML 内容
        tokens = re.split(r"(?s)({{.*?}}|{%.*?%}|{#.*?#})", text)

        for token in tokens:
            if token.startswith('{#'):
                # 忽略注释并继续
                continue
            elif token.startswith('{{'):
                # 取出执行的表达式
                expr = self._expr_code(token[2:-2].strip())
                buffered.append("to_str({0})".format(expr))
            elif token.startswith('{%'):
                # 分割语句
                flush_output()
                words = token[2:-2].strip().split()
                if words[0] == 'if':
                    # if 语句
                    if len(words) != 2:
                        self._syntax_error("Don't understand if", token)
                    ops_stack.append('if')
                    code.add_line("if {0}:".format(self._expr_code(words[1])))
                    code.indent()
                elif words[0] == 'for':
                    # for 循环
                    if len(words) != 4 or words[2] != 'in':
                        self._syntax_error("Don't understand for", token)
                    ops_stack.append('for')
                    self._variable(words[1], self.loop_vars)
                    code.add_line(
                        "for c_{0} in {1}:".format(words[1], self._expr_code(words[3])))
                    code.indent()
                elif words[0].startswith('end'):
                    if len(words) != 1:
                        self._syntax_error("Don't understand end", token)
                    end_what = words[0][3:]
                    if not ops_stack:
                        self._syntax_error("Too many ends", token)
                    start_what = ops_stack.pop()
                    if start_what != end_what:
                        self._syntax_error("Mismatched end tag", end_what)
                    code.dedent()
                else:
                    self._syntax_error("Don't understand tag", words[0])
            else:
                if token:
                    buffered.append(repr(token))

        if ops_stack:
            self._syntax_error("Unmatched action tag", ops_stack[-1])

        flush_output()

        # 定义在 all_vars 而不在 loop_vars 中的变量
        for var_name in self.all_vars - self.loop_vars:
            vars_code.add_line("c_{0} = context[{1}]".format(var_name, repr(var_name)))

        code.add_line("return ''.join(result)")
        code.dedent()
        self._render_function = code.get_globals()['render_function']

    def _expr_code(self, expr):
        """
        解析变量或表达式
        :param expr:
        :return:
        """
        if "|" in expr:
            pipes = expr.split("|")
            code = self._expr_code(pipes[0])
            for func in pipes[1:]:
                self._variable(func, self.all_vars)
                code = "c_%s(%s)" % (func, code)
        elif "." in expr:
            dots = expr.split(".")
            code = self._expr_code(dots[0])
            args = ", ".join(repr(d) for d in dots[1:])
            code = "do_dots(%s, %s)" % (code, args)
        else:
            self._variable(expr, self.all_vars)
            code = "c_%s" % expr
        return code

    @staticmethod
    def _syntax_error(msg, thing):
        """
        抛出异常
        :param msg:
        :param thing:
        :return:
        """
        raise TempliteSyntaxError("{0}: {1}".format(msg, repr(thing)))

    def _variable(self, name, vars_set):
        """
        检查变量命名
        :param name:
        :param vars_set:
        :return:
        """
        if not re.match(r"[_a-zA-Z][_a-zA-Z0-9]*$", name):
            self._syntax_error("Not a valid name", name)
        vars_set.add(name)

    def render(self, context=None):
        """
        渲染模板
        :param context:dict
        :return:
        """
        # Make the complete context we'll use.
        render_context = dict(self.context)
        if context:
            render_context.update(context)
        return self._render_function(render_context, self._do_dots)

    @staticmethod
    def _do_dots(value, *dots):
        for dot in dots:
            try:
                value = getattr(value, dot)
            except AttributeError:
                value = value[dot]
            if callable(value):
                value = value()
        return value
