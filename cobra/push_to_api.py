# -*- coding: utf-8 -*-

"""
    push_to_api
    ~~~~~~~~~~~~~~~~~~~

    Export scan result to files or console

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import json
import os
import time

import requests

from .config import Config, running_path
from .log import logger


class PushBase(object):
    def __init__(self, url):
        self.api = str(url)
        self.token = Config("third_party_vulnerabilities", "key").value
        logger.info('[PUSH API] Start pushing to third party API: {0}'.format(self.api))


class PushToThird(PushBase):
    def __init__(self, url):
        PushBase.__init__(self, url)
        self.post_data = list()

    def add_data(self, target, sid):
        """
        Add scan result to post data.
        :param target: scan target
        :param sid: scan data s_sid
        :return:
        """
        scan_data_file = os.path.join(running_path, '{sid}_data'.format(sid=sid))
        if not os.path.exists(scan_data_file):
            logger.warning('[PUSH API] No such sid.')
            return False

        with open(scan_data_file, 'r') as f:
            scan_data = json.load(f).get('result')

        scan_time = os.path.getctime(filename=scan_data_file)
        scan_time = time.localtime(scan_time)
        scan_time = time.strftime('%Y-%m-%d %H:%M:%S', scan_time)

        for i, vul in enumerate(scan_data.get('vulnerabilities')):
            self.post_data.append({
                "name": "Target-" + str(target) + '-' + str(i),
                "time": scan_time,
                "vuln_type": vul.get("rule_name"),
                "summitid": self.token,
                "signid": vul.get('id'),
                "description": '\n'.join(['{key}: {value}'.format(key=key, value=value) for key, value in vul.items()]),
            })
        return True

    def push(self):
        """
        Push data to API.
        :return: push success or not
        """

        try:
            re = requests.post(url=self.api, data={"info": json.dumps(self.post_data, ensure_ascii=False)})

            result = re.json()
            if result.get("vul_pdf", "") != "":
                logger.info('[PUSH API] Push success!')
                return True
            else:
                logger.warning('[PUSH API] Push result error: {0}'.format(re.text))
                return False
        except (requests.ConnectionError, requests.HTTPError) as error:
            logger.critical('[PUSH API] Network error: {0}'.format(str(error)))
            return False
        except ValueError as error:
            logger.critical('[PUSH API] Response error: {0}'.format(str(error)))
            return False
