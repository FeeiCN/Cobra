#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
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


#
# 61 -> 1'1''
#
def convert_time(seconds):
    one_minute = 60
    minute = seconds / one_minute
    if minute == 0:
        return str(seconds % one_minute) + "'"
    else:
        return str(minute) + "''" + str(seconds % one_minute) + "'"


#
# 123456 -> 123,456
#
def convert_number(number):
    if number is None or number == 0:
        return 0
    number = int(number)
    return '{:20,}'.format(number)


def md5(content):
    return hashlib.md5(content).hexdigest()


def allowed_file(filename):
    config_extension = config.Config('upload', 'extensions').value
    if config_extension == '':
        log.critical('Please set config file upload->directory')
        sys.exit(0)
    allowed_extensions = config_extension.split('|')
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions
