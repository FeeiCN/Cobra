#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    test
    ~~~~

    Implements the test for cobra

    :author:    Feei <feei#feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
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
            if 'result' in response_json:
                if 'project_id' in response_json['result']:
                    return response_json['result']['project_id']
            print(self.target, response_json)
            return 0
        except (requests.ConnectionError, requests.HTTPError) as e:
            self.fail("API Add failed: {0}".format(e))
            return 0

    def test_all_projects(self):
        with open('/Volumes/Statics/Downloads/all_git') as f:
            for index, line in enumerate(f):
                self.target = line.strip()
                project_id = self.test_api()
                print(index, self.target, project_id)

    def test_get_all_git_projects(self):
        project_id = 1749
        checked_id = []
        from app.models import db, CobraResults
        results = CobraResults.query.filter(CobraResults.project_id == project_id).order_by(CobraResults.id.asc()).all()
        for index, result in enumerate(results):
            if index == 0:
                checked_id.append(result.id)
            del_count = CobraResults.query.filter(
                CobraResults.project_id == project_id,
                CobraResults.rule_id == result.rule_id,
                CobraResults.file == result.file,
                CobraResults.line == result.line,
                CobraResults.status == result.status,
                CobraResults.id.notin_(checked_id)
            ).delete(synchronize_session=False)
            if del_count > 0:
                checked_id.append(result.id)
                db.session.commit()

    def test_hard_coded_password(self):
        import os
        from app.models import CobraProjects, CobraResults
        from pickup.git import Git
        from utils import config, common
        projects = CobraProjects.query.order_by(CobraProjects.id.asc()).all()
        rank = []
        offline = []
        for project in projects:
            hard_coded_password_rule_ids = [137, 135, 134, 133, 132, 130, 129, 124, 123, 122]
            count_total = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(hard_coded_password_rule_ids)).count()

            # detect project Cobra configuration file
            if project.repository[0] == '/':
                project_directory = project.repository
            else:
                project_directory = Git(project.repository).repo_directory
            cobra_properties = config.properties(os.path.join(project_directory, 'cobra'))
            need_scan = True
            if 'scan' in cobra_properties:
                need_scan = common.to_bool(cobra_properties['scan'])
            if need_scan:
                count_fixed = CobraResults.query.filter(CobraResults.project_id == project.id, CobraResults.rule_id.in_(hard_coded_password_rule_ids), CobraResults.status == 2).count()
                count_not_fixed = count_total - count_fixed
                remark = ''
            else:
                count_fixed = 0
                count_not_fixed = 0
                remark = 'offline'
            if count_total != 0:
                s = {
                    'name': project.name,
                    'id': project.id,
                    'not_fixed': count_not_fixed,
                    'fixed': count_fixed,
                    'total': count_total,
                    'remark': remark,
                    'author': project.author
                }
                if s['remark'] == 'offline':
                    offline.append(s)
                else:
                    rank.append(s)
        rank = sorted(rank, key=lambda x: x['not_fixed'], reverse=True)
        for r in rank:
            print("| [{0}](http://cobra.meili-inc.com/report/{1}) | {6} | {2} | {3} | {4} | {5} |".format(r['name'], r['id'], r['not_fixed'], r['fixed'], r['total'], r['remark'], r['author']))
        for r in offline:
            print("| [{0}](http://cobra.meili-inc.com/report/{1}) | {6} | {2} | {3} | {4} | {5} |".format(r['name'], r['id'], r['not_fixed'], r['fixed'], r['total'], r['remark'], r['author']))

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
                'code': "curl_setopt($curl, CURLOPT_URL, \"http://blog.feei.cn/ssrf\");",
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
