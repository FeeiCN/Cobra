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

find_vul = []
for i in range(4):
    srv = []
    for j in range(3):
        mr = VulnerabilityResult()
        mr.file_path = "/etc/passwd"
        mr.line_number = 182
        mr.commit_author = "author"
        mr.code_content = "<script>alert(document.cookie)</script>"
        mr.match_result = "pregex"
        mr.commit_time = "2017-04-04"
        mr.vulnerability = "xss"
        mr.rule_name = "Reflected XSS"
        srv.append(mr)
    find_vul.append(srv)


def test_push_to_api():
    pusher = PushToThird()
    pusher.add_data(find_vul=find_vul)
    assert "description" in str(pusher.post_data)
