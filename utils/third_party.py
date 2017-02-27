# -*- coding: utf-8 -*-

"""
    utils.third_party
    ~~~~~~~~~~~~~~~~~

    Implement Third-party Vulnerability Manage Push

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import json
import requests
from utils import config
from app.models import CobraResults
from app import db
from utils.log import logging

logging = logging.getLogger(__name__)


class Vulnerabilities(object):
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
            # 为杜绝前面环节问题导致输出重复,所以推送前先检查是否已经推送过
            exist_vuln = CobraResults.query.filter_by(id=self.vuln_id, status=2).count()
            if exist_vuln == 0:
                logging.info("已经推送过")
                return False
            vulns = {'info': json.dumps(self.vulnerabilities)}
            response = requests.post(self.api, data=vulns)
            if response.text == 'done':
                logging.info('推送漏洞到第三方漏洞管理平台成功')
                """
                更新漏洞状态
                1. 漏洞状态是初始化(0) -> 更新(1)
                2. 漏洞状态是已推送(1) -> 不更新
                3. 漏洞状态是已修复(2) -> 不更新
                """
                if self.vuln_id is None:
                    logging.warning("漏洞ID不能为空")
                else:
                    vuln = CobraResults.query.filter_by(id=self.vuln_id).first()
                    if vuln.status == 0:
                        vuln.status = 1
                        db.session.add(vuln)
                        db.session.commit()
                return True
            else:
                logging.critical('推送第三方漏洞管理平台失败 \r\n{0}'.format(response.text))
                return False
        except (requests.ConnectionError, requests.HTTPError) as e:
            logging.warning("推送第三方漏洞管理平台出现异常: {0}".format(e))
            return False
