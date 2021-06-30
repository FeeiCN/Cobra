# -*- coding: utf-8 -*-

"""
    export
    ~~~~~~

    Export scan result to files or console

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import csv
import json
import os
from codecs import open, BOM_UTF8

from prettytable import PrettyTable

from .config import running_path, export_path
from .log import logger

try:
    import cgi as html
except ImportError:
    import html

try:
    # Python 2
    _unicode = unicode
except NameError:
    # Python 3
    _unicode = str


def dict_to_xml(dict_obj, line_padding=''):
    """
    Convert scan result to XML string.
    :param dict_obj:a dict object
    :param line_padding:
    :return: XML String
    """
    result_list = []

    if isinstance(dict_obj, list):
        for list_id, sub_elem in enumerate(dict_obj):
            result_list.append(' ' * 4 + '<vul>')
            result_list.append(dict_to_xml(sub_elem, line_padding))
            result_list.append(' ' * 4 + '</vul>')

        return '\n'.join(result_list)

    if isinstance(dict_obj, dict):
        for tag_name in dict_obj:
            sub_obj = dict_obj[tag_name]
            if isinstance(sub_obj, _unicode):
                sub_obj = html.escape(sub_obj)
            result_list.append('%s<%s>' % (line_padding, tag_name))
            result_list.append(dict_to_xml(sub_obj, ' ' * 4 + line_padding))
            result_list.append('%s</%s>' % (line_padding, tag_name))

        return '\n'.join(result_list)

    return '%s%s' % (line_padding, dict_obj)


def dict_to_json(dict_obj):
    """
    Convert scan result to JSON string.
    :param dict_obj: a dict object
    :return: JSON String
    """
    return json.dumps(dict_obj, ensure_ascii=False)


def dict_to_csv(vul_list, filename):
    """
    Write scan result to file.
    :param vul_list:a list which contains dicts
    :param filename:
    :return:
    """
    # 排序并将 target 调整到第一列
    try:
        header = sorted(vul_list[0].keys())
        header.remove('target')
        header.insert(0, 'target')

        # 去除列表中的换行符
        for vul in vul_list:
            vul['solution'] = vul.get('solution').replace('\n', '')

        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                # 防止在 Excel 中中文显示乱码
                f.write(BOM_UTF8)
                csv_writer = csv.DictWriter(f, header)
                csv_writer.writeheader()
                csv_writer.writerows(vul_list)
                return True
        else:
            with open(filename, 'a', encoding='utf-8') as f:
                csv_writer = csv.DictWriter(f, header)
                csv_writer.writerows(vul_list)
                return True
    except IndexError:
        return False


def dict_to_pretty_table(vul_list):
    """
    Pretty print vul_list in console.
    :param vul_list:
    :return: Pretty Table Format String
    """
    row_list = PrettyTable()
    row_list.field_names = ['#', 'CVI', 'Vulnerability', 'File','Commit', 'Code Content']
    row_list.align = 'l'
    for _id, vul in enumerate(vul_list):
        row_list.add_row(
            [_id+1, vul.get('id'), vul.get('rule_name'), vul.get('file_path') + ':' + str(vul.get('line_number')),
             '@' + vul.get('commit_author')+','+vul.get('commit_time'), vul.get('code_content').strip()]
        )
    return row_list


def write_to_file(target, sid, output_format='', filename=None):
    """
    Export scan result to file.
    :param target: scan target
    :param sid: scan sid
    :param output_format: output format
    :param filename: filename to save
    :return:
    """
    if not filename:
        logger.debug('[EXPORT] No filename given, nothing exported.')
        return False

    scan_data_file = os.path.join(running_path, '{sid}_data'.format(sid=sid))
    with open(scan_data_file, 'r') as f:
        scan_data = json.load(f).get('result')

    os.chdir(export_path)
    scan_data['target'] = target

    if output_format == '' or output_format == 'stream':
        logger.info('Vulnerabilities\n' + str(dict_to_pretty_table(scan_data.get('vulnerabilities'))))

    elif output_format == 'json' or output_format == 'JSON':
        try:
            if not os.path.exists(filename):
                with open(filename, 'w', encoding='utf-8') as f:
                    json_data = {
                        sid: scan_data,
                    }
                    f.write(dict_to_json(json_data))
            else:
                with open(filename, 'r+', encoding='utf-8') as f:
                    try:
                        json_data = json.load(f)
                        json_data.update({sid: scan_data})
                        # 使用 r+ 模式不会覆盖，调整文件指针到开头
                        f.seek(0)
                        f.truncate()
                        f.write(dict_to_json(json_data))
                    except ValueError:
                        logger.warning('[EXPORT] The json file have invaild token or None: {}'.format(os.path.join(export_path, filename)))
                        return False
        except IOError:
            logger.warning('[EXPORT] Please input a file path after the -o parameter')
            return False

    elif output_format == 'xml' or output_format == 'XML':
        xml_data = {
            sid: scan_data,
        }
        if not os.path.exists(filename):
            with open(filename, 'w', encoding='utf-8') as f:
                f.write("""<?xml version="1.0" encoding="UTF-8"?>\n""")
                f.write("""<results>\n""")
                f.write(dict_to_xml(xml_data))
                f.write("""\n</results>\n""")
        else:
            # 在倒数第二行插入
            with open(filename, 'r+', encoding='utf-8') as f:
                results = f.readlines()
                results.insert(len(results) - 1, '\n' + dict_to_xml(xml_data) + '\n')
                f.seek(0)
                f.truncate()
                f.writelines(results)

    elif output_format == 'csv' or output_format == 'CSV':
        for vul in scan_data.get('vulnerabilities'):
            vul['target'] = scan_data.get('target')
        res = dict_to_csv(scan_data.get('vulnerabilities'), filename)
        if res is False:
            logger.info('[EXPORT] Not found vulnerability, Can\'t export csv file')
            return False

    else:
        logger.warning('[EXPORT] Unknown output format.')
        return False

    logger.info('[EXPORT] Scan result exported successfully: {fn}'.format(fn=export_path + '/' + filename))
    return True
