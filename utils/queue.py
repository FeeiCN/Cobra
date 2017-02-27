# -*- coding: utf-8 -*-

"""
    utils.queue
    ~~~~~~~~~~~

    Implement Vulnerability Push Queue

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import time
from daemon import push_vulnerabilities, error_handler
from utils.third_party import Vulnerabilities


class Queue(object):
    def __init__(self, project_name, vuln_name, vuln_type, file_path, line_number, code, vuln_id, found_time=None):
        self.project_name = project_name
        self.vuln_name = vuln_name
        self.vuln_type = vuln_type
        self.file_path = file_path
        self.line_number = line_number
        self.code = code
        self.vuln_id = vuln_id
        if found_time is None:
            current_time = time.strftime('%Y-%m-%d %X', time.localtime())
            self.time = current_time
        else:
            self.time = found_time

    def push(self):
        v = Vulnerabilities()
        data = [{
            "name": "{0}项目{1}漏洞({2})".format(self.project_name, self.vuln_name, self.vuln_id),
            "time": self.time,
            "vuln_type": self.vuln_type,
            "filepath": self.file_path,
            "linenum": self.line_number,
            "code": "\r\n\r\n{0}".format(self.code),
            "summitid": v.key,
            "signid": self.vuln_id,
            'description': '\r\n\r\n该漏洞由Cobra(代码安全审计系统)自动发现并报告!'
        }]
        push_vulnerabilities.apply_async(data, link_error=error_handler.s(), serializer='json')
