# coding=utf-8
from config import Config
from log import logger
from export import flatten
import requests
import json


class PushBase(object):
    def __init__(self):
        self.api = Config("third_party_vulnerabilities", "api").value
        self.token = Config("third_party_vulnerabilities", "key").value
        logger.info("Start pushing to third party API: {0}".format(self.api))


class PushToHades(PushBase):
    """Push vulnerabilities to Hades."""

    def __init__(self):
        PushBase.__init__(self)
        self.post_data = None

    def add_data(self, find_vul):
        self.post_data = []
        for vul in flatten(find_vul):
            self.post_data.append({
                "name": "MVE-" + str(vul.get("id")),
                "time": vul.get("timestamp"),
                "vuln_type": vul.get("type"),
                "summitid": self.token,
                "signid": vul.get("id"),
                "description": vul.get("match_result")
            })

    def push(self):
        """
        Push data tu API.
        :param find_vul: scan result, need to be flattened first
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
        except (requests.ConnectionError, requests.HTTPError), error:
            logger.critical("Network error: {0}".format(str(error)))
            return False
        except ValueError, error:
            logger.critical("Response error: {0}".format(str(error)))
            return False
