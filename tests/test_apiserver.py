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

import requests
from cobra.api import start
import json
import multiprocessing
import os

# test apiserver after creating config file.

p = multiprocessing.Process(target=start, args=("127.0.0.1", 5000, True))
p.start()


def test_add_job():
    # url = "http://127.0.0.1:5000/api/add"
    # post_data = {
    #     "key": "your_secret_key",
    #     "target": ["https://github.com/wufeifei/grw.git", "https://github.com/shadowsocks/shadowsocks.git"],
    # }
    # headers = {
    #     "Content-Type": "application/json",
    # }
    # re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    # assert "1001" in re.content
    # assert "Add scan job successfully" in re.content
    # assert "sid" in re.content
    pass


def test_job_status():
    # url = "http://127.0.0.1:5000/api/status"
    # post_data = {
    #     "key": "your_secret_key",
    #     "sid": 24,
    # }
    # headers = {
    #     "Content-Type": "application/json",
    # }
    # re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    # assert "1001" in re.content
    # assert "msg" in re.content
    # assert "sid" in re.content
    # assert "status" in re.content
    # assert "report" in re.content
    pass


p.terminate()
