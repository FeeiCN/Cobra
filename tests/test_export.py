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
        mr.label = "xss"
        mr.rule_name = "Reflected XSS"
        srv.append(mr)
    find_vul.append(srv)

vul_list = export.flatten(find_vul)
write_obj = {"Vuls": vul_list}


def test_export_to_html():
    html_string = export.dict_to_html(vul_list)
    # HTML header
    assert "<!DOCTYPE html>" in html_string
    # code_content
    assert "document.cookie" in html_string
    # line_number
    assert "182" in html_string
    # file_path
    assert "/etc/passwd" in html_string
    # commit_author
    assert "author" in html_string
    # match_result
    assert "pregex" in html_string
    # commit_time
    assert "2017-04-04" in html_string
    # vulnerability
    assert "xss" in html_string
    # rule_name
    assert "Reflected XSS" in html_string


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
    # vulnerability
    assert "xss" in json_string
    # rule_name
    assert "Reflected XSS" in json_string


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
    # vulnerability
    assert "xss" in xml_string
    # rule_name
    assert "Reflected XSS" in xml_string


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
    assert "author" in table_string
    # commit_time
    assert "2017-04-04" in table_string
    # vulnerability
    assert "xss" in table_string
