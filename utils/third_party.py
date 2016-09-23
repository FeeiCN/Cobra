# -*- coding: utf-8 -*-

"""
    utils.third_party
    ~~~~~~~~~~~~~~~~~

    实现第三方漏洞管理平台对接

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import json
import requests
import logging
from utils import config
from app import CobraResults, db


class Vulnerabilities:
    def __init__(self):
        self.status = config.Config('third_party_vulnerabilities', 'status').value
        self.api = config.Config('third_party_vulnerabilities', 'api').value
        self.key = config.Config('third_party_vulnerabilities', 'key').value

        self.vulnerabilities = []
        self.vuln_id = []

    def add(self, vulnerabilities_info):
        self.vuln_id.append(vulnerabilities_info['signid'])
        self.vulnerabilities.append(vulnerabilities_info)

    def push(self):
        try:
            vulns = {'info': json.dumps(self.vulnerabilities)}
            response = requests.post(self.api, data=vulns)
            if response.text == 'done':
                logging.info('Push third vulnerabilities success')
                # update vulnerabilities status
                if self.vuln_id is None:
                    logging.warning("Vuln ID is none")
                else:
                    vuln = CobraResults.query.filter_by(id=self.vuln_id).first()
                    vuln.status = 1
                    db.session.add(vuln)
                    db.session.commit()
                return True
            else:
                logging.critical('Push third vulnerabilities failed \r\n{0}'.format(response.text))
                return False
        except (requests.ConnectionError, requests.HTTPError) as e:
            logging.warning("API Add failed: {0}".format(e))
            return False
