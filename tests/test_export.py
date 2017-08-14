# -*- coding: utf-8 -*-

"""
    tests.export
    ~~~~~~~~~~~~

    Tests cobra.export

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from cobra import export
from cobra.result import VulnerabilityResult
import json
import random

find_vul = []
for j in range(10):
    mr = VulnerabilityResult()
    mr.id = str(random.randint(1000, 9999))
    mr.language = 'php'
    mr.rule_name = 'xss'
    mr.file_path = '/etc/passwd'
    mr.line_number = 182
    mr.code_content = '<script>alert(document.cookie)</script>'
    mr.match_result = 'pregex'
    mr.level = '2'
    mr.commit_time = '2017-04-04'
    mr.commit_author = 'test'

    find_vul.append(mr)

vul_list = [x.__dict__ for x in find_vul]
target = "https://github.com/test/test.git"
write_obj = {
    "target": target,
    "vulnerabilities": vul_list,
}


def test_export_to_json():
    json_string = export.dict_to_json(write_obj)
    # JSON format
    assert isinstance(json.loads(json_string), dict)
    # code_content
    assert "document.cookie" in json_string
    # line_number
    assert "182" in json_string
    # file_path
    assert "/etc/passwd" in json_string
    # commit_author
    assert "author" in json_string
    # match_result
    assert "pregex" in json_string
    # commit_time
    assert "2017-04-04" in json_string
    # rule_name
    assert "xss" in json_string


def test_export_to_xml():
    xml_string = export.dict_to_xml(write_obj)
    # XML tag
    assert "</" in xml_string
    # code_content
    assert "document.cookie" in xml_string
    # line_number
    assert "182" in xml_string
    # file_path
    assert "/etc/passwd" in xml_string
    # commit_author
    assert "author" in xml_string
    # match_result
    assert "pregex" in xml_string
    # commit_time
    assert "2017-04-04" in xml_string
    # rule_name
    assert "xss" in xml_string


def test_export_to_pretty_table():
    """
    Only export id, vulnerability, file_path, line_number, commit_time, commit_author
    :return:
    """
    table_string = str(export.dict_to_pretty_table(vul_list))
    # PrettyTable format
    assert "|" in table_string
    # file_path
    assert "/etc/passwd" in table_string
    # line_number
    assert "182" in table_string
    # commit_author
    assert "Author" in table_string
    # commit_time
    assert "2017-04-04" in table_string
    # vulnerability
    assert "xss" in table_string
