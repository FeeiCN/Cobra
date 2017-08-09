# -*- coding: utf-8 -*-

"""
    tests.pushapi
    ~~~~~~~~~~~~

    Tests cobra.push_to_api

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from cobra.push_to_api import PushToThird
from cobra.result import VulnerabilityResult
import json

find_vul = []
for i in range(4):
    srv = []
    for j in range(3):
        mr = VulnerabilityResult()
        mr.id = '12001'
        mr.file_path = '/index.php'
        mr.rule_name = '硬编码密码'
        mr.language = 'php'
        mr.line_number = 182
        mr.code_content = '$password = "12345"'
        mr.match_result = "pregex"
        mr.level = None
        mr.commit_time = '2017-04-04'
        mr.commit_author = 'author'
        srv.append(mr)
    find_vul.append(srv)


def test_push_to_api():
    pusher = PushToThird()
    pusher.add_data(target='https://github.com/test/test.git', find_vul=find_vul)
    assert 'https://' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '2017-04-04' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '硬编码密码' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'summitid' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'description' in json.dumps(pusher.post_data, ensure_ascii=False)
