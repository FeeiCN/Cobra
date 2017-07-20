# -*- coding: utf-8 -*-

"""
    export
    ~~~~~~~~~~~~~~~~~~~

    Export scan result to files or console

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import json
import os
import csv
from .log import logger
from prettytable import PrettyTable
from templite import Templite

try:
    # python 3
    import html
except ImportError:
    # python 2
    import cgi as html


def dict_to_xml(dict_obj, line_padding=""):
    """
    Convert scan result to XML string.
    :param dict_obj:a dict object
    :param line_padding:
    :return: XML String
    """
    result_list = []

    if isinstance(dict_obj, list):
        for list_id, sub_elem in enumerate(dict_obj):
            result_list.append(" " * 4 + "<Vulnerability-" + str(list_id) + ">")
            result_list.append(dict_to_xml(sub_elem, line_padding))
            result_list.append(" " * 4 + "</Vulnerability-" + str(list_id) + ">")

        return "\n".join(result_list)

    if isinstance(dict_obj, dict):
        for tag_name in dict_obj:
            sub_obj = dict_obj[tag_name]
            if isinstance(sub_obj, str):
                sub_obj = html.escape(sub_obj)
            result_list.append("%s<%s>" % (line_padding, tag_name))
            result_list.append(dict_to_xml(sub_obj, " " * 4 + line_padding))
            result_list.append("%s</%s>" % (line_padding, tag_name))

        return "\n".join(result_list)

    return "%s%s" % (line_padding, dict_obj)


def dict_to_json(dict_obj):
    """
    Convert scan result to JSON string.
    :param dict_obj:a dict object
    :return: JSON String
    """
    return json.dumps(dict_obj)


def dict_to_csv(vul_list, filename):
    """
    Write scan result to file.
    :param vul_list:a list which contains dicts
    :param filename:
    :return:
    """
    with open(filename, "w") as f:
        csv_writer = csv.DictWriter(f, vul_list[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(vul_list)


def dict_to_html(vul_list):
    """
    Convert scan result to HTML string.
    :param vul_list:a list which contains dicts
    :return: HTML String
    """
    print os.path.dirname(__file__)
    with open(os.path.join(os.path.dirname(__file__), "templates/asset/js/report.js"), "r") as f:
        report_js = f.read()

    # 计算 vid 对应的数组偏移，统计 vul_list 中的 mode，type
    rule_filter, type_filter = set(), set()
    for index, value in enumerate(vul_list):
        rule_filter.add(value.get("rule_name"))
        type_filter.add(value.get("vulnerability"))

    with open(os.path.join(os.path.dirname(__file__), "templates/export.html"), "r") as f:
        template = f.read()

    templite = Templite(template)
    html_content = templite.render({
        "vul_list": html.escape(json.dumps(vul_list)),
        "rule_filter": list(rule_filter),
        "type_filter": list(type_filter),
        "report_js": report_js
    })
    return html_content


def dict_to_pretty_table(vul_list):
    """
    Pretty print vul_list in console.
    :param vul_list:
    :return: Pretty Table Format String
    """
    row_list = PrettyTable()
    row_list.field_names = ["ID", "Vulnerability", "Target", "Discover Time", "Author"]
    for vul in vul_list:
        row_list.add_row(
            [vul.get("id"), vul.get("vulnerability"), vul.get("file_path") + ": " + str(vul.get("line_number")),
             vul.get("commit_time"),
             vul.get("commit_author")])
    return row_list


def flatten(input_list):
    """
    flatten vul_list and change items to dicts using convert_to_dict method.
    :param input_list:
    :return: output_list
    """
    output_list = []
    while True:
        if not input_list:
            break
        for index, i in enumerate(input_list):
            if isinstance(i, list):
                input_list = i + input_list[index + 1:]
                break
            else:
                output_list.append(i.convert_to_dict())
                input_list.pop(index)
                break
    return output_list


def write_to_file(find_vuls, output_format="", filename=""):
    """
    Export scan result to file.
    :param find_vuls: list of scan result
    :param output_format: output format
    :param filename: filename to save
    :return:
    """

    # find_vuls
    """
    [
        [mr, mr, mr],
        [mr, mr, mr],
        [mr, mr, mr]
    ]

    where
    mr = {"file_path": "xxxx", "code_content": "<?php phpinfo();?>"}, which is a dict.
    """

    vul_list = flatten(find_vuls)
    write_obj = {"Vuls": vul_list}

    if output_format == "":
        logger.info("Vulnerabilites\n" + str(dict_to_pretty_table(vul_list)))

    elif output_format == "json" or output_format == "JSON":
        with open(filename, "w") as f:
            f.write(dict_to_json(write_obj))

    elif output_format == "xml" or output_format == "XML":
        with open(filename, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
            f.write(dict_to_xml(write_obj))

    elif output_format == "csv" or output_format == "CSV":
        dict_to_csv(vul_list, filename)

    elif output_format == "html" or output_format == "HTML":
        with open(filename, "w") as f:
            f.write(dict_to_html(vul_list))

    else:
        raise ValueError("Unknown output format!")
