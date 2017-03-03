# -*- coding: utf-8 -*-

"""
    utils.common
    ~~~~~~~~~~~~

    Implements common helpers

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import sys
import datetime
import hashlib
from utils import config
from utils.log import logging

logging = logging.getLogger(__name__)


def convert_time(seconds):
    """
    Seconds to minute/second
    Ex: 61 -> 1′1″
    :param seconds:
    :return:
    :link: https://en.wikipedia.org/wiki/Prime_(symbol)
    """
    one_minute = 60
    minute = seconds / one_minute
    if minute == 0:
        return str(seconds % one_minute) + "″"
    else:
        return str(minute) + "′" + str(seconds % one_minute) + "″"


def convert_number(number):
    """
    Convert number to , split
    Ex: 123456 -> 123,456
    :param number:
    :return:
    """
    if number is None or number == 0:
        return 0
    number = int(number)
    return '{:20,}'.format(number).strip()


def md5(content):
    """
    MD5 Hash
    :param content:
    :return:
    """
    return hashlib.md5(content).hexdigest()


def allowed_file(filename):
    """
    Allowd upload file
    Config Path: ./config [upload]
    :param filename:
    :return:
    """
    config_extension = config.Config('upload', 'extensions').value
    if config_extension == '':
        logging.critical('Please set config file upload->directory')
        sys.exit(0)
    allowed_extensions = config_extension.split('|')
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


def to_bool(value):
    """
       Converts 'something' to boolean. Raises exception for invalid formats
           Possible True  values: 1, True, "1", "TRue", "yes", "y", "t"
           Possible False values: 0, False, None, [], {}, "", "0", "faLse", "no", "n", "f", 0.0, ...
    """
    if str(value).lower() in ("yes", "y", "true", "t", "1"): return True
    if str(value).lower() in ("no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"): return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def path_to_short(path, max_length=36):
    """
    /impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java
    /impl/src/.../utils/CertUtil.java
    :param path:
    :param max_length:
    :return:
    """
    if len(path) < max_length:
        return path
    paths = path.split('/')
    paths = filter(None, paths)
    tmp_path = ''
    for i in range(0, len(paths)):
        # print(i, str(paths[i]), str(paths[len(paths) - i - 1]))
        tmp_path = tmp_path + str(paths[i]) + '/' + str(paths[len(paths) - i - 1])
        if len(tmp_path) > max_length:
            tmp_path = ''
            for j in range(0, i):
                tmp_path = tmp_path + '/' + str(paths[j])
            tmp_path += '/...'
            for k in range(i, 0, -1):
                tmp_path = tmp_path + '/' + str(paths[len(paths) - k])
            if tmp_path == '/...':
                return '.../{0}'.format(paths[len(paths) - 1])
            elif tmp_path[0] == '/':
                return tmp_path[1:]
            else:
                return tmp_path


def path_to_file(path):
    """
    Path to file
    /impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java
    .../CertUtil.java
    :param path:
    :return:
    """
    paths = path.split('/')
    paths = filter(None, paths)
    return '.../{0}'.format(paths[len(paths) - 1])


def percent(part, whole, need_per=True):
    """
    Percent
    :param part:
    :param whole:
    :param need_per:
    :return:
    """
    if need_per:
        per = '%'
    else:
        per = ''
    if part == 0 and whole == 0:
        return 0
    return '{0}{1}'.format(100 * float(part) / float(whole), per)


def format_gmt(time_gmt, time_format=None):
    """
    Format GMT time
    Ex: Wed, 14 Sep 2016 17:57:41 GMT to 2016-09-14 17:57:41
    :param time_gmt:
    :param time_format:
    :return:
    """
    import time
    if time_format is None:
        time_format = '%Y-%m-%d %X'
    t = time.strptime(time_gmt, "%a, %d %b %Y %H:%M:%S GMT")
    return time.strftime(time_format, t)
