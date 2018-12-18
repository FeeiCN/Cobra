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


class CobraScan(object):
    def __init__(self):
        # 漏洞信息
        self.id = 140007
        self.language = "JAVA"
        self.author = "BlBana"
        self.email = "blbana@qq.com"
        self.name = "直接输出入参可能导致XSS"
        self.level = 4
        self.solution = '''
            ## 安全风险
            直接输出入参会导致XSS

            ## 修复方案
            使用Begis安全组件对参数进行过滤后使用
        '''

        # status
        self.status = True

        # 漏洞规则
        self.match_mode = "plugins-ast"
        self.match = "setAttribute|getWriter|write|append"
        self.java_rule = ['setAttribute:javax.servlet.http.HttpServletRequest',
                          'getWriter:javax.servlet.http.HttpServletResponse',
                          'write:javax.servlet.http.HttpServletResponse',
                          'append:javax.servlet.http.HttpServletResponse']

    def verify(self):
        """
        regex string input
        :regex_string: regex match string
        :return:
        """
        status = False
        result = {
            'status': status,  # verify验证是否成功
            'msg': 'test'
        }
        return result
