# -*- coding: utf-8 -*-

"""
    engine.dependency
    ~~~~~~~~~~~~~~~~~

    Implements dependency analysis

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import re
import subprocess
import traceback
from utils.config import Config
from utils.queue import Queue
from packaging import version
from app.models import db, CobraResults
from utils.log import logging

logging = logging.getLogger(__name__)

# `mvn`
mvn = ['/usr/local/bin/mvn', '/usr/local/maven/bin/mvn']


class Dependency(object):
    def __init__(self, result_info=None, dependencies=None, test=False):
        self.data = []
        self.result = result_info
        self.dependencies = dependencies
        self.test = test

        self.mvn = None
        for mvn_path in mvn:
            if os.path.isfile(mvn_path):
                self.mvn = mvn_path
        if self.mvn is None:
            self.mvn = 'mvn'
            self.log('critical', 'mvn not found')

        self.current_groupId = None
        self.current_artifactId = None
        self.current_version = None

        self.trigger_groupId = None
        self.trigger_artifactId = None
        self.trigger_operator = None
        self.trigger_version = None

        self.file = None

    def log(self, level, message):
        if self.test:
            self.data.append('[{0}] {1}'.format(level.upper(), message))
        if level == 'critical':
            logging.critical(message)
        elif level == 'warning':
            logging.warning(message)
        elif level == 'info':
            logging.info(message)
        elif level == 'debug':
            logging.debug(message)
        elif level == 'error':
            logging.error(message)

    def parse_rule(self, rule):
        """
        Parse rule
            groupId:artifactId[operator]version
            Operator: > < = >= <=
            E.g:
            com.alibaba:fastjson=1.1.24
        :return: groupId, artifactId, operator, version
        """
        lrs = rule.split(':')
        av = re.findall(r'(.*)([<>=]+)(.*)', lrs[1])
        if len(av) == 1:
            artifact_id, operator, version = av[0]
            self.log('info', 'Parse rule: {0} {1} {2} {3}'.format(lrs[0], artifact_id, operator, version))
            return lrs[0], artifact_id, operator, version
        else:
            self.log('critical', 'Parse rule failed(rule format error): {rule}'.format(rule=rule))
            return None

    def list(self, directory):
        """
        Analysis project's dependency
        :return: dependency list 
        """
        dependencies = {}
        pom = os.path.join(directory, 'pom.xml')
        if os.path.isfile(pom) is not True:
            return dependencies
        param = [self.mvn, "dependency:list"]
        p = subprocess.Popen(param, stdout=subprocess.PIPE, cwd=directory)
        result = p.communicate()
        if len(result[0]):
            for line in result[0].splitlines():
                line = str(line).strip()
                print(line)
                jar = re.findall(r'\[INFO\]\s(.*):(?=compile|test|runtime|provided)', line)
                if len(jar) == 1:
                    pieces = jar[0].strip().split(":")
                    key = '{0}_{1}_{2}'.format(pieces[0], pieces[1], pieces[3])
                    if key not in dependencies:
                        dependencies[key] = {
                            'groupId': pieces[0],
                            'artifactId': pieces[1],
                            'version': pieces[3]
                        }
        return dependencies

    def process_vulnerability(self):
        exist_result = CobraResults.query.filter(
            CobraResults.project_id == self.result['project_id'],
            CobraResults.rule_id == self.result['rule_id'],
        ).first()
        if exist_result is None:
            if self.test:
                self.log('info', '[RET] insert vulnerability\r\n')
            else:
                self.file = '{0}:{1}({2})'.format(self.current_groupId, self.current_artifactId, self.current_version)
                vul = CobraResults(self.result['rule_id'], self.result['project_id'], self.result['rule_id'], self.file, 0, '', 0, CobraResults.get_status('init'))
                db.session.add(vul)
                db.session.commit()
                self.log('info', "insert new vulnerabilities VID: {0}".format(vul.id))
                self.push_third_party_vulnerabilities(vul.id)
        else:
            if exist_result.status == CobraResults.get_status('fixed'):
                if self.test is not True:
                    exist_result.status = CobraResults.get_status('init')
                    exist_result.repair = 0
                    db.session.add(exist_result)
                    db.session.commit()
                self.log('info', '[RET] This vulnerabilities already exist(Fixed) and update status(Not Fixed)!')

    def push_third_party_vulnerabilities(self, vulnerabilities_id):
        """
        Pushed to a third-party vulnerability management platform
        :param vulnerabilities_id:
        :return:
        """
        try:
            status = Config('third_party_vulnerabilities', 'status').value
            if int(status):
                q = Queue(self.result['project_name'], self.result['third_party_vulnerabilities_name'], self.result['third_party_vulnerabilities_type'], self.file, 0, '', vulnerabilities_id)
                q.push()
        except Exception as e:
            traceback.print_exc()
            self.log('critical', e.message)

    def check(self):
        # trigger dependency
        ret_trigger = self.parse_rule(self.result['regex_location'])
        if ret_trigger is None:
            self.log('info', 'Parse rule failed')
            return self.data
        else:
            self.trigger_groupId, self.trigger_artifactId, self.trigger_operator, self.trigger_version = ret_trigger

        # current dependency
        if len(self.dependencies) == 0:
            c = 'Not found any dependencies'
            self.log('info', c)
            return self.data
        for k, dl in self.dependencies.items():
            if dl['groupId'] == self.trigger_groupId and dl['artifactId'] == self.trigger_artifactId:
                self.current_groupId = dl['groupId']
                self.current_artifactId = dl['artifactId']
                self.current_version = dl['version']

        # have trigger dependency(have same groupId and artifactId)
        if self.current_groupId is None and self.current_artifactId is None:
            c = 'Not found trigger dependency'
            self.log('info', c)
            return self.data

        self.log('info', 'Current project: {0} {1} {2}'.format(self.current_groupId, self.current_artifactId, self.current_version))
        # is trigger(compare version)
        msg = '{0} {1} {2}'.format(self.current_version, self.trigger_operator, self.trigger_version)
        if self.trigger_operator == '>=':
            ret = version.parse(self.current_version) >= version.parse(self.trigger_version)
        elif self.trigger_operator == '<=':
            ret = version.parse(self.current_version) <= version.parse(self.trigger_version)
        elif self.trigger_operator == '>':
            ret = version.parse(self.current_version) > version.parse(self.trigger_version)
        elif self.trigger_operator == '<':
            ret = version.parse(self.current_version) < version.parse(self.trigger_version)
        elif self.trigger_operator == '=':
            ret = version.parse(self.current_version) == version.parse(self.trigger_version)
        else:
            self.log('critical', 'Exception operation')
            ret = False
        self.log('info', 'Is vulnerability: {0} {1}'.format(ret, msg))
        if ret:
            self.process_vulnerability()
        return self.data

    @staticmethod
    def is_dependency_rule(rule):
        """
        Is Dependency Rule
        
        :rule:
            [\w\.]*:[\w\-\.]*[<>=]*[\d\.]*
            com.alibaba:fastjson=1.1.24
            com.alibaba:fastjson<1.1.24
            com.alibaba:fastjson<1.1.24
            com.alibaba:fastjson>=1.2.29
            com.alibaba:fastjson<=1.2.29
            com.alibaba:fast-json<=1.2.29
            com.alibaba:fast.json<=1.2.29
            com.alibaba:fast_json<=1.2.29
        :param: self.location_rule
        :return: boolean 
        """
        is_dependency_rule = r'[\w\.]*:[\w\-\.]*[<>=]*[\d\.]*'
        idr = re.findall(is_dependency_rule, rule)
        return len(idr) >= 1
