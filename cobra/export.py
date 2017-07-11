# coding=utf-8
import json
import csv

try:
    # python 3
    import html
except ImportError:
    # python 2
    import cgi as html


def dict_to_xml(dict_obj, line_padding=""):
    """
    Convert a dict object to XML string.
    :param dict_obj:
    :param line_padding:indent
    :return: XML string
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
    Convert a dict object to JSON string.
    :param dict_obj:
    :return: JSON string
    """
    return json.dumps(dict_obj)


def dict_to_csv(vul_list, filename):
    """
    Write a list which contains dicts to file.
    :param vul_list:
    :param filename:
    :return:
    """
    with open(filename, "w") as f:
        csv_writer = csv.DictWriter(f, vul_list[0].keys())
        csv_writer.writeheader()
        csv_writer.writerows(vul_list)


def dict_to_html(vul_list):
    """
    Convert a list which contains dicts to HTML string.
    :param vul_list:
    :return: HTML String
    """
    result_list = []
    html_header = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vulnerabilities List</title>
</head>
<body>\n"""
    result_list.append(html_header)
    result_list.append("<ul>\n")
    for list_id, dict_obj in enumerate(vul_list):
        result_list.append(" " * 4 + "<li>Vulnerability - " + str(list_id + 1) + "\n")
        result_list.append(" " * 4 * 2 + "<ul>\n")
        for k, v in dict_obj.items():
            result_list.append(" " * 4 * 3 + "<li>" + html.escape(str(k)) + ": ")
            result_list.append(html.escape(str(v)))
            result_list.append("</li>\n")
        result_list.append(" " * 4 * 2 + "</ul>\n")
        result_list.append(" " * 4 * 1 + "</li>\n")
    result_list.append(" " * 4 + "</ul>\n")
    html_footer = """</body>
</html>"""
    result_list.append(html_footer)

    return "".join(result_list)


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


def write_to_file(find_vuls, output_format, filename):
    """
    Export scan result to file.
    :param find_vuls: 扫描结果的 list
    :param output_format: 输出格式
    :param filename: 保存的文件名
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

    if output_format == "json":
        with open(filename, "w") as f:
            f.write(dict_to_json(write_obj))

    elif output_format == "xml":
        with open(filename, "w") as f:
            f.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
            f.write(dict_to_xml(write_obj))

    elif output_format == "csv":
        dict_to_csv(vul_list, filename)

    elif output_format == "html":
        with open(filename, "w") as f:
            f.write(dict_to_html(vul_list))
