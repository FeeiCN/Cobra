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
import random

find_vul = []
for j in range(10):
    mr = VulnerabilityResult()
    mr.id = str(random.randint(1000, 9999))
    mr.language = 'php'
    mr.rule_name = '硬编码密码'
    mr.file_path = '/etc/passwd'
    mr.line_number = 182
    mr.code_content = '<script>alert(document.cookie)</script>'
    mr.match_result = 'pregex'
    mr.level = '2'
    mr.commit_time = '2017-04-04'
    mr.commit_author = 'test'

    find_vul.append(mr)

find_vul = [x.__dict__ for x in find_vul]


def test_push_to_api():
    pusher = PushToThird()
    pusher.add_data(target='https://github.com/test/test.git', find_vul=find_vul)
    assert 'https://' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '2017-04-04' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '硬编码密码' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'summitid' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'description' in json.dumps(pusher.post_data, ensure_ascii=False)
