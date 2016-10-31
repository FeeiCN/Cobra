#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test
    ~~~~

    Implements the test for cobra

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""

import unittest
import requests
from utils import common, config
import json


class Test(unittest.TestCase):
    domain = '{0}:{1}'.format(config.Config('cobra', 'host').value, config.Config('cobra', 'port').value)
    api = 'http://' + domain + '/api/{0}'
    headers = {"Content-Type": "application/json"}

    key = common.md5('CobraAuthKey')
    target = 'https://github.com/wufeifei/dict.git'
    branch = 'master'

    def test_api(self):
        """
        Cobra API Test
        :return:
        """
        payload = json.dumps({
            "key": self.key,
            "target": self.target,
            "branch": self.branch
        })

        try:
            response = requests.post(self.api.format('add'), data=payload, headers=self.headers)
            response_json = response.json()
            code = response_json.get('code')
            print(code)
            # self.assertEqual(code, 1001)
        except (requests.ConnectionError, requests.HTTPError) as e:
            self.fail("API Add failed: {0}".format(e))

    def test_all_projects(self):
        with open('/Volumes/Statics/Downloads/all-projects.txt') as f:
            for index, line in enumerate(f):
                self.target = line.strip()
                print(index, self.target)
                self.test_api()

    def test_push(self):
        from daemon import push_vulnerabilities, error_handler
        from utils.third_party import Vulnerabilities
        v = Vulnerabilities()
        data = [{
            "name": "Cobra发现(/path/to/mogujie)项目一处SSRF漏洞",
            "time": "2016-09-12 17:01:40",
            "vuln_type": "10000000",
            "filepath": "/path/to/test.php",
            "linenum": "123",
            "code": "\r\n\r\n$str = $_GET['test'];\r\necho $str;",
            "summitid": v.key,
            "signid": '12',
            'description': '\r\n\r\n该漏洞由Cobra(代码安全审计系统)自动发现并报告!'
        }]
        push_vulnerabilities.apply_async(data, link_error=error_handler.s(), serializer='json')

    def test_config(self):
        from utils.config import Config
        status = Config('third_party_vulnerabilities', 'status').value
        self.assertTrue(int(status))

    def test_parse4java(self):
        """
        测试解析规则(Java)
        :return:
        """
        import os
        from engine.parse import Parse
        regex_location = r'new\sURL\((.*)\)'
        regex_repair = r'Security.filter\({{PARAM}}\)'
        file_path = os.path.join(config.Config().project_directory, 'tests/parse/test_functions.java')
        tests = [
            {
                'line': 33,
                'code': "URL obj = new URL(url);",
                'result': False,
            },
            {
                'line': 66,
                'code': "URL obj = new URL(url);",
                'result': False,
                'repair': True
            }
        ]
        for test in tests:
            parse = Parse(regex_location, file_path, test['line'], test['code'])
            self.assertEqual(test['result'], parse.is_controllable_param())
            if 'repair' in test:
                self.assertEqual(test['repair'], parse.is_repair(regex_repair, 0))

    def test_parse4php(self):
        """
        测试解析规则(PHP)
        :return:
        """
        import os
        from engine.parse import Parse
        regex_location = r'curl_setopt\s?\(.*,\s?CURLOPT_URL\s?,(.*)\)'
        regex_repair = r'curl_setopt\s?\(.*,\s?CURLOPT_PROTOCOLS\s?,(.*)\)'
        file_path = os.path.join(config.Config().project_directory, 'tests/parse/test_functions.php')
        tests = [
            {
                'line': 4,
                'code': "curl_setopt($curl, CURLOPT_URL, \"http://wufeifei.com/ssrf\");",
                'result': False,
            },
            {
                'line': 10,
                'code': 'curl_setopt($curl, CURLOPT_URL, URL);',
                'result': False
            },
            {
                'line': 16,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': False
            },
            {
                'line': 22,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': True,
                'repair': False
            },
            {
                'line': 28,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': True,
                'repair': True
            }
        ]
        for test in tests:
            parse = Parse(regex_location, file_path, test['line'], test['code'])
            self.assertEqual(test['result'], parse.is_controllable_param())
            if 'repair' in test:
                self.assertEqual(test['repair'], parse.is_repair(regex_repair, 1))

        file_path = os.path.join(config.Config().project_directory, 'tests/parse/test_single_file.php')
        tests = [
            {
                'line': 4,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': False
            },
            {
                'line': 8,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': True
            },
            {
                'line': 12,
                'code': 'curl_setopt($curl, CURLOPT_URL, $url);',
                'result': True,
                'repair': True
            }
        ]
        for test in tests:
            parse = Parse(regex_location, file_path, test['line'], test['code'])
            self.assertEqual(test['result'], parse.is_controllable_param())
            if 'repair' in test:
                self.assertEqual(test['repair'], parse.is_repair(regex_repair, 1))


if __name__ == '__main__':
    unittest.main()
