# -*- coding: utf-8 -*-

"""
    tests.export
    ~~~~~~~~~~~~

    Tests cobra.export

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import json
import os

from cobra.config import running_path, export_path
from cobra.export import write_to_file, dict_to_pretty_table

scan_data_file = os.path.join(running_path, 'abcdefg_data')
if not os.path.exists(scan_data_file):
    with open(scan_data_file, 'w') as f:
        scan_data = r"""{"code": 1001, "msg": "scan finished", "result": {"extension": 18, "file": 132, "framework": "Unknown Framework", "language": "python", "push_rules": 43, "target_directory": "/tmp/cobra/git/shadowsocks/shadowsocks/", "trigger_rules": 1, "vulnerabilities": [{"code_content": "    assert '127.0.1.1' not in ip_network", "commit_author": "Sunny", "commit_time": "2015-01-31 19:50:10", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "294", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.168.1.2' not in ip_network", "commit_author": "Sunny", "commit_time": "2015-01-31 19:50:10", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "300", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.0.2.1' in ip_network", "commit_author": "Sunny", "commit_time": "2015-02-01 00:17:03", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "301", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "    assert '192.0.3.1' in ip_network  # 192.0.2.0 is treated as 192.0.2.0/23", "commit_author": "Sunny", "commit_time": "2015-02-01 00:17:03", "file_path": "shadowsocks/common.py", "id": "130005", "language": "*", "level": "4", "line_number": "302", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}, {"code_content": "                IPNetwork(config.get('forbidden_ip', '127.0.0.0/8,::1/128'))", "commit_author": "loggerhead", "commit_time": "2016-11-20 14:59:32", "file_path": "shadowsocks/shell.py", "id": "130005", "language": "*", "level": "4", "line_number": "146", "match_result": null, "rule_name": "\u786c\u7f16\u7801IP", "solution": "## \u5b89\u5168\u98ce\u9669\n        \u786c\u7f16\u7801IP\n\n        ## \u4fee\u590d\u65b9\u6848\n        \u79fb\u5230\u914d\u7f6e\u6587\u4ef6\u4e2d"}]}}"""
        f.write(scan_data)

target = "https://github.com/test/test.git"


def test_export_to_json():
    write_to_file(target=target, sid='abcdefg', output_format='json', filename='test.json')
    assert os.path.exists(os.path.join(export_path, 'test.json'))

    with open(os.path.join(export_path, 'test.json')) as f:
        json_string = f.read()
    # JSON format
    assert isinstance(json.loads(json_string), dict)
    # code_content
    assert "127.0.1.1" in json_string
    # line_number
    assert "294" in json_string
    # file_path
    assert "common.py" in json_string
    # commit_author
    assert "Sunny" in json_string
    # commit_time
    assert "2015-01-31" in json_string
    # rule_name
    assert "硬编码IP" in json_string

    os.remove(os.path.join(export_path, 'test.json'))


def test_export_to_xml():
    write_to_file(target=target, sid='abcdefg', output_format='xml', filename='test.xml')
    assert os.path.exists(os.path.join(export_path, 'test.xml'))

    with open(os.path.join(export_path, 'test.xml')) as f:
        xml_string = f.read()
    # XML tag
    assert "</" in xml_string
    # code_content
    assert "127.0.1.1" in xml_string
    # line_number
    assert "294" in xml_string
    # file_path
    assert "common.py" in xml_string
    # commit_author
    assert "Sunny" in xml_string
    # commit_time
    assert "2015-01-31" in xml_string
    # rule_name
    assert "硬编码IP" in xml_string

    os.remove(os.path.join(export_path, 'test.xml'))


def test_export_to_pretty_table():
    """
    Only export id, vulnerability, file_path, line_number, commit_time, commit_author
    :return:
    """
    scan_data_file = os.path.join(running_path, '{sid}_data'.format(sid='abcdefg'))
    with open(scan_data_file, 'r') as f:
        scan_data = json.load(f).get('result')

    table_string = str(dict_to_pretty_table(scan_data.get('vulnerabilities')))
    # PrettyTable format
    assert "|" in table_string
    # file_path
    assert "common.py" in table_string
    # line_number
    assert "294" in table_string
    # commit_author
    assert "Sunny" in table_string
    # commit_time
    assert "2015-01-31" in table_string
    # vulnerability
    assert "硬编码IP" in table_string
