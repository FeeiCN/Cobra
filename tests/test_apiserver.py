# -*- coding: utf-8 -*-

"""
    tests.apiserver
    ~~~~~~~~~~~~

    Tests cobra.api

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""

# 测试完成需要手动关闭 API server 和扫描进程
# kill -9 $(ps aux|grep test_apiserver.py|awk '{print $2}')
# kill -9 $(ps aux|grep cobra.py|awk '{print $2}')
# 第一次启动 server 测试可能会卡住

import requests
from cobra.api import start
import json

start(host="127.0.0.1", port=5000, debug=True)


def test_add_job():
    url = "http://127.0.0.1:5000/api/add"
    post_data = {
        "key": "your_secret_key",
        "target": "https://github.com/wufeifei/grw.git",
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    assert "1001" in re.content
    assert "Add scan job successfully" in re.content
    assert "scan_id" in re.content


def test_job_status():
    url = "http://127.0.0.1:5000/api/status"
    post_data = {
        "key": "your_secret_key",
        "scan_id": 24,
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    print re.content
    assert "1001" in re.content
    assert "msg" in re.content
    assert "scan_id" in re.content
    assert "status" in re.content
    assert "report" in re.content
