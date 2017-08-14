# -*- coding: utf-8 -*-

"""
    push_to_api
    ~~~~~~~~~~~~~~~~~~~

    Export scan result to files or console

    :author:    40huo <git@40huo.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from .config import Config
from .log import logger
import requests
import json


class PushBase(object):
    def __init__(self):
        self.api = Config("third_party_vulnerabilities", "api").value
        self.token = Config("third_party_vulnerabilities", "key").value
        logger.info("Start pushing to third party API: {0}".format(self.api))


class PushToThird(PushBase):
    def __init__(self):
        PushBase.__init__(self)
        self.post_data = None

    def add_data(self, target, find_vul):
        self.post_data = []
        for i, vul in enumerate(find_vul):
            self.post_data.append({
                "name": "Target-" + str(target) + '-' + str(i),
                "time": vul.get("commit_time"),
                "vuln_type": vul.get("rule_name"),
                "summitid": self.token,
                "signid": str(i),
                "description": vul.get("rule_name")
            })

    def push(self):
        """
        Push data to API.
        :return: push success or not
        """

        try:
            re = requests.post(url=self.api, data={"info": json.dumps(self.post_data)})

            result = re.json()
            if result.get("vul_pdf", "") != "":
                logger.info("Push success!")
                return True
            else:
                logger.debug("Push result error: {0}".format(re.text))
                return False
        except (requests.ConnectionError, requests.HTTPError)as error:
            logger.critical("Network error: {0}".format(str(error)))
            return False
        except ValueError as error:
            logger.critical("Response error: {0}".format(str(error)))
            return False
