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
    Convert a dict object to JSON string.
    :param dict_obj:
    :return: JSON String
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
    with open("report.js", "r") as f:
        report_js = "<script>\n" + f.read() + "</script>"
    html_header = """<!doctype html>
<html>
<head>
    <meta charset="utf-8">
    <title>Vulnerabilities List</title>
    <link rel="stylesheet" href="./templates/asset/css/base.css">
    <link rel="stylesheet" href="./templates/asset/css/report.css">
    <script src="./templates/asset/js/jquery-1.11.2.min.js"></script>
    <script src="./templates/asset/codemirror/lib/codemirror.js"></script>
    <link rel="stylesheet" href="./templates/asset/codemirror/lib/codemirror.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/theme/material.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/addon/fold/foldgutter.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/addon/dialog/dialog.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/addon/search/matchesonscrollbar.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/addon/scroll/simplescrollbars.css">
    <link rel="stylesheet" href="./templates/asset/codemirror/addon/display/fullscreen.css">
    <script src="./templates/asset/codemirror/addon/fold/foldcode.js"></script>
    <script src="./templates/asset/codemirror/addon/fold/foldgutter.js"></script>
    <script src="./templates/asset/codemirror/addon/fold/markdown-fold.js"></script>
    <script src="./templates/asset/codemirror/addon/fold/comment-fold.js"></script>
    <script src="./templates/asset/codemirror/addon/fold/xml-fold.js"></script>
    <script src="./templates/asset/codemirror/addon/fold/brace-fold.js"></script>
    <script src="./templates/asset/codemirror/addon/display/placeholder.js"></script>
    <script src="./templates/asset/codemirror/addon/display/fullscreen.js"></script>
    <script src="./templates/asset/codemirror/addon/display/panel.js"></script>
    <script src="./templates/asset/codemirror/addon/edit/matchbrackets.js"></script>
    <script src="./templates/asset/codemirror/addon/edit/matchtags.js"></script>
    <script src="./templates/asset/codemirror/addon/dialog/dialog.js"></script>
    <script src="./templates/asset/codemirror/addon/search/searchcursor.js"></script>
    <script src="./templates/asset/codemirror/addon/search/search.js"></script>
    <script src="./templates/asset/codemirror/addon/scroll/annotatescrollbar.js"></script>
    <script src="./templates/asset/codemirror/addon/search/matchesonscrollbar.js"></script>
    <script src="./templates/asset/codemirror/addon/search/jump-to-line.js"></script>
    <script src="./templates/asset/codemirror/addon/search/match-highlighter.js"></script>
    <script src="./templates/asset/codemirror/addon/scroll/simplescrollbars.js"></script>
    <script src="./templates/asset/codemirror/addon/selection/active-line.js"></script>
    <script src="./templates/asset/codemirror/mode/markdown/markdown.js"></script>
    <script src="./templates/asset/codemirror/mode/javascript/javascript.js"></script>
    <script src="./templates/asset/codemirror/mode/css/css.js"></script>
    <script src="./templates/asset/codemirror/mode/xml/xml.js"></script>
    <script src="./templates/asset/codemirror/mode/yaml/yaml.js"></script>
    <script src="./templates/asset/codemirror/mode/htmlmixed/htmlmixed.js"></script>
    <script src="./templates/asset/codemirror/mode/php/php.js"></script>
    <script src="./templates/asset/codemirror/mode/python/python.js"></script>
    <script src="./templates/asset/codemirror/mode/ruby/ruby.js"></script>
    <script src="./templates/asset/codemirror/mode/perl/perl.js"></script>
    <script src="./templates/asset/codemirror/mode/lua/lua.js"></script>
    <script src="./templates/asset/codemirror/mode/go/go.js"></script>
    <script src="./templates/asset/codemirror/mode/cmake/cmake.js"></script>
    <script src="./templates/asset/codemirror/mode/shell/shell.js"></script>
    <script src="./templates/asset/codemirror/mode/sql/sql.js"></script>
    <script src="./templates/asset/codemirror/mode/clike/clike.js"></script>
</head>
<body>"""
    result_list.append(html_header)

    # 原始数据写入 JS 变量
    result_list.append("<script>\nvar vul_list_origin=" + html.escape(str(vul_list)) + ";")

    # 计算 vid 对应的数组偏移，统计 vul_list 中的 mode，type
    mode_filter, type_filter = set(), set()
    vid_list = dict()
    for index, value in enumerate(vul_list):
        vid_list[value["id"]] = index
        mode_filter.add(value["mode"])
        type_filter.add(value["type"])
    result_list.append("var vid_list=" + html.escape(str(vid_list)) + ";")
    result_list.append("var mode_filter=" + html.escape(str(list(mode_filter))) + ";")
    result_list.append("var type_filter=" + html.escape(str(list(type_filter))) + ";\n</script>")

    html_vul_list = """<div class="container-fluid">
    <div class="row">
        <div class="col-xs-12">
            <div class="invoice-title">
                <h2>Cobra</h2>
            </div>
            <hr>
            <ul class="nav nav-tabs">
                <li class="active"><a data-id="vul" data-toggle="tab">Vulnerabilities</a></li>
            </ul>
            <div class="tab-content">
                <div class="tab-pane active" id="vul">
                    <div class="row">
                        <div class='col-md-3 p0'>
                        <div id="panel-2" class="vl_panel"><strong>Vulnerabilities</strong><a title="Setting vulnerabilities filter" class="cog-panel filter_setting"><img class="icon" src="./templates/asset/icon/funnel.png" alt="1"></a></div>
                        <div class="filter">
                            <div class="col-md-12" style="margin-top: 10px;">
                                <label for="search_vul_type" style="color: #aaaaaa;">Types</label>
                                <select id="search_vul_type" class="form-control" style="height: 30px;">
                                    <option value="all">All</option>\n"""

    for type in type_filter:
        html_vul_list += " " * 4 * 9 + "<option value=\"" + type + "\">" + type + "</option>\n"
    html_vul_list += """                                </select>
                            </div>
                            <div class="col-md-12" style="margin-top: 10px">
                                <label for="search_rule" style="color: #aaaaaa;">Mode</label>
                                <select id="search_rule" class="form-control" style="height: 30px;">
                                    <option value="all">All</option>\n"""
    for mode in mode_filter:
        html_vul_list += " " * 4 * 9 + "<option value=\"" + mode + "\">" + mode + "</option>\n"
    html_vul_list += """                                </select>
                            </div>
                            <div class="col-md-12" style="margin-top: 10px;">
                                <label for="search_level" style="color: #aaaaaa;">Level</label>
                                <select id="search_level" class="form-control" style="height: 30px;">
                                    <option value="all">All</option>
                                    <option value="3">High</option>
                                    <option value="2">Medium</option>
                                    <option value="1">Low</option>
                                </select>
                            </div>
                            <div class="col-md-12" style="padding:20px 30%">
                                <button class="btn btn-success filter_btn" style="">Summit filter</button>
                            </div>
                        </div>
                        <ul class='vulnerabilities_list scroll'>
                        </ul>
                    </div>
                    <div class='col-md-9 p0 form_code'>
                        <textarea id='code'><?php // This is a demo code</textarea>
                        <div class='cm-loading' style='display:none;'></div>
                    </div>
                </div>
            </div>
        </div>
        </div>
    </div>
    <div class="widget-list">
        <ul class="widget-trigger">
            <li>
                <img class="icon" src="./templates/asset/icon/v-card.png" alt="Commit Author"> <span class="commit-author"></span> <img class="icon" src="./templates/asset/icon/calendar.png" alt="Commit Time"> <span class="commit-time"></span>
            </li>
            <li>
                Status: <span class="v-status"></span> (<span class="v-repair"></span>)
            </li>
            <li>
                Level: <span class="v-level"></span> <span class="v-type"></span> - <span class="v-rule"></span> By <span class="v-rule-author"></span>
            </li>
            <li>
                Repair AT: <span class="v-repair-time"></span> Repair: <span class="v-repair-description"></span>
            </li>
            <li class="hidden">
                Score: <span></span> CWE: <span></span> OWASP Top10: <span></span> SANA 25 Rank: <span></span> Bounty: <span></span>
            </li>
        </ul>
    </div>
"""
    result_list.append(html_vul_list)
    html_footer = """    <div class="row">
        <div class="col-md-6">
            <div>
                <p style="float:left;">
                    Copyright &copy; 2017 <a href="https://github.com/wufeifei/cobra" target="_blank">Cobra</a>. All rights reserved
                </p>
            </div>
        </div>
        <div class="col-md-6">
            <div>
                <p style="float:right;">
                    <a href="https://github.com/wufeifei/cobra" target="_blank">Github</a> -
                    <a href="http://cobra-docs.readthedocs.io/" target="_blank">Documents</a> -
                    <a href="http://cobra.feei.cn/" target="_blank">About</a>
                </p>
            </div>
        </div>
    </div>
</body>
</html>"""
    result_list.append(report_js)

    result_list.append(html_footer)

    return "\n".join(result_list)


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
