# -*- coding: utf-8 -*-

"""
    utils.common
    ~~~~~~~~~~~~

    Implements common helpers

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import sys
import datetime
import hashlib
from utils import config, log


def convert_timestamp(stamp):
    """returns a datetime.date object off a timestamp"""
    # Really, this should be implemented using time.strptime()
    date_shards = stamp.split()
    date_shards = date_shards[0].split('-')
    date_shards = [x.lstrip('0') for x in date_shards]
    processed_date = datetime.date(int(date_shards[0]), int(date_shards[1]), int(date_shards[2]))
    return processed_date


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
    return '{:20,}'.format(number)


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
        log.critical('Please set config file upload->directory')
        sys.exit(0)
    allowed_extensions = config_extension.split('|')
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions
