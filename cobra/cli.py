# -*- coding: utf-8 -*-

"""
    cli
    ~~~

    Implements CLI mode

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from .pickup import Directory
from .utils import ParseArgs
from .detection import Detection
from .engine import scan, Running
from .log import logger
from .utils import md5, random_generator


def get_sid(target, is_a_sid=False):
    # target = target.encode('utf-8')
    if isinstance(target, list):
        target = ';'.join(target)
    sid = md5(target)[:5]
    if is_a_sid:
        pre = 'a'
    else:
        pre = 's'
    sid = '{p}{sid}{r}'.format(p=pre, sid=sid, r=random_generator())
    return sid.lower()


def start(target, formatter, output, special_rules, a_sid=None):
    """
    Start CLI
    :param target: File, FOLDER, GIT
    :param formatter:
    :param output:
    :param special_rules:
    :param a_sid: all scan id
    :return:
    """
    # generate single scan id
    s_sid = get_sid(target)
    r = Running(a_sid)
    data = r.init_list()
    data['sids'].append(s_sid)
    r.init_list(data)

    # parse target mode and output mode
    pa = ParseArgs(target, formatter, output, special_rules, a_sid=None)
    target_mode = pa.target_mode
    output_mode = pa.output_mode

    # target directory
    target_directory = pa.target_directory(target_mode)

    # static analyse files info
    files, file_count, time_consume = Directory(target_directory).collect_files()

    # detection main language and framework
    dt = Detection(target_directory, files)
    main_language = dt.language
    main_framework = dt.framework

    logger.info('[CLI] [STATISTIC] Language: {l} Framework: {f}'.format(l=main_language, f=main_framework))
    logger.info('[CLI] [STATISTIC] Files: {fc}, Extensions:{ec}, Consume: {tc}'.format(fc=file_count, ec=len(files), tc=time_consume))

    if pa.special_rules is not None:
        logger.info('[CLI] [SPECIAL-RULE] only scan used by {r}'.format(r=','.join(pa.special_rules)))

    # scan
    scan(target_directory, a_sid, s_sid, pa.special_rules)
