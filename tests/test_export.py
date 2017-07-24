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
    assert "document.cookie" in export.dict_to_html(vul_list)


def test_export_to_json():
    assert isinstance(json.loads(export.dict_to_json(write_obj)), dict)


def test_export_to_xml():
    assert "</" in export.dict_to_xml(write_obj)


def test_export_to_pretty_table():
    assert "|" in str(export.dict_to_pretty_table(vul_list))
