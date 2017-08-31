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
import re

from .detection import Detection
from .engine import scan, Running
from .exceptions import PickupException
from .export import write_to_file
from .log import logger
from .pickup import Directory
from .send_mail import send_mail
from .utils import ParseArgs
from .utils import md5, random_generator
from .push_to_api import PushToThird


def get_sid(target, is_a_sid=False):
    target = target
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
    data = (s_sid, target)
    r.init_list(data=target)
    r.list(data)

    report = '?sid={a_sid}'.format(a_sid=a_sid)
    d = r.status()
    d['report'] = report
    r.status(d)

    # parse target mode and output mode
    pa = ParseArgs(target, formatter, output, special_rules, a_sid=None)
    target_mode = pa.target_mode
    output_mode = pa.output_mode

    # target directory
    try:
        target_directory = pa.target_directory(target_mode)
        logger.info('[CLI] Target directory: {d}'.format(d=target_directory))

        # static analyse files info
        files, file_count, time_consume = Directory(target_directory).collect_files()

        # detection main language and framework
        dt = Detection(target_directory, files)
        main_language = dt.language
        main_framework = dt.framework

        logger.info('[CLI] [STATISTIC] Language: {l} Framework: {f}'.format(l=main_language, f=main_framework))
        logger.info('[CLI] [STATISTIC] Files: {fc}, Extensions:{ec}, Consume: {tc}'.format(fc=file_count,
                                                                                           ec=len(files),
                                                                                           tc=time_consume))

        if pa.special_rules is not None:
            logger.info('[CLI] [SPECIAL-RULE] only scan used by {r}'.format(r=','.join(pa.special_rules)))

        # scan
        scan(target_directory=target_directory, a_sid=a_sid, s_sid=s_sid, special_rules=pa.special_rules,
             language=main_language, framework=main_framework, file_count=file_count, extension_count=len(files))
    except PickupException:
        result = {
            'code': 1002,
            'msg': 'Repository not exist!'
        }
        Running(s_sid).data(result)
        raise
    except Exception:
        result = {
            'code': 1002,
            'msg': 'Exception'
        }
        Running(s_sid).data(result)
        raise

    # 匹配邮箱地址
    if re.match(r'^[A-Za-z\d]+([-_.][A-Za-z\d]+)*@([A-Za-z\d]+[-.])+[A-Za-z\d]{2,4}$', output):
        # 生成邮件附件
        attachment_name = s_sid + '.' + formatter
        write_to_file(target=target, sid=s_sid, output_format=formatter, filename=attachment_name)
        # 发送邮件
        send_mail(target=target, filename=attachment_name, receiver=output)
    elif output.startswith('http'):
        # HTTP API URL
        pusher = PushToThird(url=output)
        pusher.add_data(target=target, sid=s_sid)
        pusher.push()
    else:
        write_to_file(target=target, sid=s_sid, output_format=formatter, filename=output)
