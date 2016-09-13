# -*- coding: utf-8 -*-

"""
    utils.third_party
    ~~~~~~~~~~~~~~~~~

    Implements third party (bugs manage)

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


if __name__ == '__main__':
    from utils import log

    log.Log()
    vuln = Vulnerabilities()
    data = {
        "name": "Cobra发现(/path/to/mogujie)项目一处SSRF漏洞",
        "time": "2016-09-12 17:01:40",
        "vuln_type": "10000000",
        "filepath": "/path/to/test.php",
        "linenum": "123",
        "code": "\r\n\r\n$str = $_GET['test'];\r\necho $str;",
        "summitid": vuln.key,
        "signid": '12',
        'description': '\r\n\r\n该漏洞由Cobra(代码安全审计系统)自动发现并报告!'
    }
    vuln.add(data)
    vuln.push()
