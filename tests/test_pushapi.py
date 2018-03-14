# -*- coding: utf-8 -*-

"""
    tests.pushapi
    ~~~~~~~~~~~~

    Tests cobra.push_to_api

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import json
import os

from cobra.config import running_path
from cobra.push_to_api import PushToThird

scan_data_file = os.path.join(running_path, 'abcdefg_data')
if not os.path.exists(scan_data_file):
    with open(scan_data_file, 'w') as f:
        scan_data = r"""{"code": 1001, "msg": "scan finished", "result": {"extension": 18, "file": 132, "framework": "Unknown Framework", "language": "python", "push_rules": 43, "target_directory": "/tmp/cobra/git/shadowsocks/shadowsocks/", "trigger_rules": 1, "vulnerabilities": [{"code_content": "    assert '127.0.1.1' not in ip_network", "commit_author": "Sunny", "commit_time": "2015-01-31 19:50:10", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "294", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.168.1.2' not in ip_network", "commit_author": "Sunny", "commit_time": "2015-01-31 19:50:10", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "300", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.0.2.1' in ip_network", "commit_author": "Sunny", "commit_time": "2015-02-01 00:17:03", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "301", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.0.3.1' in ip_network  # 192.0.2.0 is treated as 192.0.2.0/23", "commit_author": "Sunny", "commit_time": "2015-02-01 00:17:03", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "302", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "                IPNetwork(config.get('forbidden_ip', '127.0.0.0/8,::1/128'))", "commit_author": "loggerhead", "commit_time": "2016-11-20 14:59:32", "file_path": "shadowsocks/shell.py", "id": "130005", "language": "*", "level": "4", "line_number": "146", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}]}}"""
        f.write(scan_data)


def test_push_to_api():
    pusher = PushToThird(url='https://github.com/WhaleShark-Team/cobra')
    pusher.add_data(target='https://github.com/test/test.git', sid='abcdefg')
    assert 'https://' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '2015-01-31' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert '硬编码IP' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'summitid' in json.dumps(pusher.post_data, ensure_ascii=False)
    assert 'description' in json.dumps(pusher.post_data, ensure_ascii=False)
