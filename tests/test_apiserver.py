# -*- coding: utf-8 -*-

"""
    tests.apiserver
    ~~~~~~~~~~~~

    Tests cobra.api

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""

import json
import multiprocessing
import os
import shutil
import socket
import time

import requests

from cobra.api import start
from cobra.config import project_directory, running_path

p = multiprocessing.Process(target=start, args=('127.0.0.1', 5000, False))
p.start()
time.sleep(1)

config_path = os.path.join(project_directory, 'config')
template_path = os.path.join(project_directory, 'config.template')
shutil.copyfile(template_path, config_path)

a_sid = ''
s_sid = ''


def test_add_job():
    url = "http://127.0.0.1:5000/api/add"
    post_data = {
        "key": "your_secret_key",
        "target": "https://github.com/BlBana/Cobra_tests.git"
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    result = json.loads(re.text)

    global a_sid
    a_sid = result.get('result').get('sid')

    a_sid_file = os.path.join(running_path, '{sid}_list'.format(sid=a_sid))

    # wait writing scan_list
    while True:
        with open(a_sid_file, 'r') as f:
            scan_list = json.load(f)
            print(scan_list)
        if len(scan_list.get('sids')) > 0:
            break
        time.sleep(0.1)

    global s_sid
    s_sid = list(scan_list.get('sids').keys())[0]

    assert "1001" in re.text
    assert "Add scan job successfully" in re.text
    assert "sid" in re.text


def test_job_status():
    url = "http://127.0.0.1:5000/api/status"
    post_data = {
        "key": "your_secret_key",
        "sid": a_sid,
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)
    assert "1001" in re.text
    assert "msg" in re.text
    assert a_sid in re.text
    assert "status" in re.text
    assert "report" in re.text


def test_result_data():
    url = 'http://127.0.0.1:5000/api/list'
    post_data = {
        'sid': s_sid,
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)

    s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
    if os.path.exists(s_sid_file):
        assert '1001' in re.text
        assert 'result' in re.text
        assert 'rule_filter' in re.text
    else:
        assert '1002' in re.text
        assert 'No such target' in re.text


def test_result_detail():
    url = 'http://127.0.0.1:5000/api/detail'
    post_data = {
        'sid': s_sid,
        'file_path': 'v.php',
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)

    s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
    if os.path.exists(s_sid_file):
        assert '1001' in re.text
        assert 'file_content' in re.text
    else:
        assert '1002' in re.text
        assert 'No such target' in re.text


def test_search():
    url = 'http://127.0.0.1:5000/api/search'
    post_data = {
        'sid': s_sid,
        'rule_id': ["110001", "110005"],
    }
    headers = {
        "Content-Type": "application/json",
    }
    re = requests.post(url=url, data=json.dumps(post_data), headers=headers)

    s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
    if os.path.exists(s_sid_file):
        assert '1001' in re.text
        assert 'search_result' in re.text
    else:
        assert '1002' in re.text
        assert 'No such sid' in re.text


def test_get_member():
    url = 'http://127.0.0.1:5000/api/members'
    param1 = '?repo-url=https://github.com/WhaleShark-Team/cobra.git'
    param2 = '?repo-url=gitlab.com/xxxxx/iiiddd.git'
    req1 = requests.get(url=url + param1)
    req2 = requests.get(url=url + param2)

    assert '1002' in req1.text
    assert '1002' in req2.text


def test_report():
    url = 'http://127.0.0.1:5000/report'
    req = requests.get(url=url, timeout=3)

    assert 'Cobra Report' in req.text


def test_index():
    url = 'http://127.0.0.1:5000/'
    re = requests.get(url=url)
    assert 'Github / Gitlab' in re.text

    url = 'http://127.0.0.1:5000/?sid=abcde'
    re = requests.get(url=url)
    assert 'scan id does not exist!' in re.text


def test_close_api():
    os.remove(config_path)
    p.terminate()
    p.join()

    # wait for scan data
    s_sid_file = os.path.join(running_path, '{sid}_data'.format(sid=s_sid))
    while not os.path.exists(s_sid_file):
        time.sleep(1)

    # wait for port closed
    s = socket.socket()
    s.settimeout(0.5)
    while s.connect_ex(('localhost', 5000)) == 0:
        time.sleep(0.5)

    assert not os.path.exists(config_path)
