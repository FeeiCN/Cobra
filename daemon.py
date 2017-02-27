# -*- coding: utf-8 -*-

"""
    daemon
    ~~~~~~

    Implement Asynchronous Queue Push System
    - Third-party vulnerability manage system

    celery -A daemon worker --loglevel=info

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from celery import Celery
from utils.third_party import Vulnerabilities
from utils import config
from utils.log import logging

logging = logging.getLogger(__name__)

app = Celery('daemon', broker=config.Config('queue', 'broker').value, backend=config.Config('queue', 'backend').value)


@app.task
def push_vulnerabilities(vulnerabilities_info):
    v = Vulnerabilities()
    v.add(vulnerabilities_info)
    return v.push()


@app.task(bind=True)
def error_handler(self, uuid):
    result = self.app.AsyncResult(uuid)
    logging.critical('Task {0} raised exception: {1!r}\n{2!r}'.format(uuid, result.result, result.traceback))
