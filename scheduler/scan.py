# -*- coding: utf-8 -*-

"""
    scheduler.scan
    ~~~~~~~~~~~~~~

    Implements periodic scan job

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import json
import requests
from utils.log import logging
from utils import common, config
from app.models import CobraProjects

logging = logging.getLogger(__name__)


class Scan(object):
    def __init__(self):
        domain = '{0}:{1}'.format(config.Config('cobra', 'host').value, config.Config('cobra', 'port').value)
        self.api = 'http://' + domain + '/api/{0}'
        self.headers = {"Content-Type": "application/json"}
        self.key = common.md5('CobraAuthKey')
        self.branch = 'master'

    def all(self):
        projects = CobraProjects.query.with_entities(CobraProjects.repository).filter(CobraProjects.status == CobraProjects.get_status('on')).all()
        for project in projects:
            payload = json.dumps({
                "key": self.key,
                "target": project.repository,
                "branch": self.branch
            })

            try:
                response = requests.post(self.api.format('add'), data=payload, headers=self.headers)
                response_json = response.json()
                logging.info(project.repository, response_json)
            except (requests.ConnectionError, requests.HTTPError) as e:
                logging.critical("API Add failed: {0}".format(e))
