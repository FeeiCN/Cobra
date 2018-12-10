# -*- coding: utf-8 -*-

"""
    rule
    ~~~~

    Implements rule(languages/frameworks/vulnerabilities/rules)

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
from . import const
from .config import rules_path, plugins_path
from .log import logger
from .utils import to_bool
from xml.etree import ElementTree


def block(index):
    default_index_reverse = 'in-function'
    default_index = 0
    blocks = {
        'in-function-up': 0,
        'in-function-down': 1,
        'in-current-line': 2,
        'in-function': 3,
        'in-class': 4,
        'in-class-up': 5,
        'in-class-down': 6,
        'in-file': 7,
        'in-file-up': 8,
        'in-file-down': 9
    }
    if isinstance(index, int):
        blocks_reverse = dict((v, k) for k, v in blocks.items())
        if index in blocks_reverse:
            return blocks_reverse[index]
        else:
            return default_index_reverse
    else:
        if index in blocks:
            return blocks[index]
        else:
            return default_index


class Rule(object):
    def __init__(self):
        self.rules_path = rules_path
        self.plugins_path = plugins_path

    @property
    def languages(self):
        """
        Get all languages
        :return:
        {
            'php':{
                'chiefly': 'true',
                'extensions':[
                    '.php',
                    '.php3',
                    '.php4',
                    '.php5'
                ]
            }
        }
        """
        language_extensions = {}
        xml_languages = self._read_xml('languages.xml')
        if xml_languages is None:
            logger.critical('languages read failed!!!')
            return None
        for language in xml_languages:
            l_name = language.get('name').lower()
            l_chiefly = 'false'
            if language.get('chiefly') is not None:
                l_chiefly = language.get('chiefly')
            language_extensions[l_name] = {
                'chiefly': l_chiefly,
                'extensions': []
            }
            for lang in language:
                l_ext = lang.get('value').lower()
                language_extensions[l_name]['extensions'].append(l_ext)
        return language_extensions

    @property
    def frameworks(self):
        """
        Read all framework rules
        :return: dict
        """
        frameworks_rules = {}
        xml_frameworks = self._read_xml('frameworks.xml')
        if xml_frameworks is None:
            logger.critical('frameworks read failed!!!')
            return None
        for framework in xml_frameworks:
            f_name = framework.get('name').lower()
            f_lang = framework.get('language').lower()
            f_code = framework.get('code')
            framework_info = {
                f_name: {
                    'code': f_code,
                    'rules': []
                }
            }
            frameworks_rules[f_lang] = framework_info
            for rule in framework:
                rule_info = {rule.tag: rule.get('value')}
                frameworks_rules[f_lang][f_name]['rules'].append(rule_info)
        return frameworks_rules

    @property
    def vulnerabilities(self):
        """
        Read all vulnerabilities information
        :return:
        """
        vulnerabilities_info = {}
        xml_vulnerabilities = self._read_xml('vulnerabilities.xml')
        if xml_vulnerabilities is None:
            logger.critical('vulnerabilities read failed!!!')
            return None
        for vulnerability in xml_vulnerabilities:
            v_id = int(vulnerability.get('vid'))
            v_name = vulnerability.get('name').upper()
            vulnerabilities_info[str(v_id)] = v_name
        return vulnerabilities_info

    @property
    def sources(self):
        """
        Read all sources function rule
        :return: Dict, {package1: [method1, method2, method3], package2: [method1, method2, method3]}
        """
        source_rules = {}
        xml_sources = self._read_xml('sources.xml')
        if xml_sources is None:
            logger.critical('sources read failed !!!')
        for source in xml_sources:
            for rule in source:
                s_rule = rule.get('value')
                s_class = rule.get('class')
                source_rules.setdefault(s_class, []).append(s_rule)

        return source_rules

    def rules(self, rules=None):
        """
        Get all rules
        :return: dict
        """
        vulnerabilities = []
        if rules is not None and len(rules) > 0:
            files = rules
        else:
            files = os.listdir(self.rules_path)
        for vulnerability_name in files:
            # VN: CVI-190001.xml
            v_path = os.path.join(self.rules_path, vulnerability_name.replace('cvi', 'CVI'))
            if vulnerability_name.lower()[0:7] == 'cvi-999':
                logger.debug('filter dependency rules')
            elif 'cvi' not in v_path.lower():
                continue
            if os.path.isfile(v_path) is not True or '.xml' not in v_path.lower():
                logger.warning('Not regular rule file {f}'.format(f=v_path))
                continue

            # rule information
            rule_info = {
                'id': None,
                'file': v_path,
                'name': None,
                'language': None,
                'match': None,
                'match-mode': 'regex-only-match',
                'match2': None,
                'match2-block': None,
                'java-rules': [],
                'repair': None,
                'repair-block': None,
                'level': None,
                'solution': None,
                'test': {
                    'true': [],
                    'false': []
                },
                'status': False,
                'author': None
            }
            xml_rule = self._read_xml(v_path)
            if xml_rule is None:
                logger.critical('rule read failed!!! ({file})'.format(file=v_path))
                continue
            cvi = v_path.lower().split('cvi-')[1][:6]
            rule_info['id'] = cvi
            for x in xml_rule:
                if x.tag == 'name':
                    rule_info['name'] = x.get('value')
                if x.tag == 'language':
                    rule_info['language'] = x.get('value').lower()
                if x.tag == 'status':
                    rule_info['status'] = to_bool(x.get('value'))
                if x.tag == 'author':
                    name = x.get('name').encode('utf-8')
                    email = x.get('email')
                    rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
                if x.tag in ['match', 'match2', 'repair']:
                    if x.text is not None:
                        rule_info[x.tag] = x.text.strip()
                    if x.tag == 'match':
                        if x.get('mode') is None:
                            logger.warning('unset match mode attr (CVI-{cvi})'.format(cvi=cvi))
                        if x.get('mode') not in const.match_modes:
                            logger.warning('mode exception (CVI-{cvi})'.format(cvi=cvi))
                        rule_info['match-mode'] = x.get('mode')
                    elif x.tag == 'repair':
                        rule_info['repair-block'] = block(x.get('block'))
                    elif x.tag == 'match2':
                        rule_info['match2-block'] = block(x.get('block'))
                if x.tag == 'rules':
                    for rule in x:
                        method_name = rule.get('value')
                        class_name = rule.get('class')
                        rule_info['java-rules'].append(method_name + ':' + class_name)
                if x.tag == 'level':
                    rule_info['level'] = x.get('value')
                if x.tag == 'solution':
                    rule_info['solution'] = x.text.strip()
                if x.tag == 'test':
                    for case in x:
                        case_ret = case.get('assert').lower()
                        case_test = ''
                        if case.text is not None:
                            case_test = case.text.strip()
                        if case_ret in ['true', 'false']:
                            rule_info['test'][case_ret].append(case_test)
            vulnerabilities.append(rule_info)
        return vulnerabilities

    def plugins(self):
        """
        Get all plugins
        :return:
        """
        vulnerabilities = []
        files = os.listdir(self.plugins_path)
        for vulnerability_name in files:
            v_path = os.path.join(self.plugins_path, vulnerability_name)
            if os.path.isfile(v_path) is not True or '.py' not in v_path.lower() or '__init__' in v_path.lower() or \
                    '.pyc' in v_path.lower():
                if '__init__' in v_path.lower() or '.pyc' in v_path.lower():
                    continue
                logger.warning('Not regular plugin file {f}'.format(f=v_path))
                continue

            # rule information
            rule_info = {
                'id': None,
                'file': v_path,
                'name': None,
                'language': None,
                'match': None,
                'match-mode': 'regex-only-match',
                'match2': None,
                'match2-block': None,
                'java-rules': [],
                'repair': None,
                'repair-block': None,
                'level': None,
                'solution': None,
                'test': {
                    'true': [],
                    'false': []
                },
                'status': False,
                'author': None
            }
            plugins_name = os.path.splitext(os.path.basename(v_path))[0]
            plugins_file = 'plugins.' + plugins_name
            plugins = __import__(plugins_file, fromlist=[plugins_name])
            plugin = plugins.CobraScan()
            if plugin is None:
                logger.critical('Plugin read failed!!! ({file})'.format(file=v_path))
                continue
            rule_info['id'] = str(plugin.id)

            if hasattr(plugin, 'name'):
                rule_info['name'] = plugin.name
            if hasattr(plugin, 'language'):
                rule_info['language'] = plugin.language.lower()
            if hasattr(plugin, 'status'):
                rule_info['status'] = to_bool(plugin.status)
            if hasattr(plugin, 'author') and hasattr(plugin, 'email'):
                name = plugin.author.encode('utf-8')
                email = plugin.email
                rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
            if hasattr(plugin, 'java_rule'):
                rule_info['java-rules'] = plugin.java_rule
            if hasattr(plugin, 'level'):
                rule_info['level'] = plugin.level
            if hasattr(plugin, 'solution'):
                rule_info['solution'] = plugin.solution.strip()
            if hasattr(plugin, 'match'):
                rule_info['match'] = plugin.match
            if hasattr(plugin, 'match_mode'):
                rule_info['match-mode'] = plugin.match_mode
            vulnerabilities.append(rule_info)
        return vulnerabilities

    def _read_xml(self, filename):
        """
        Read XML
        :param filename:
        :return:
        """
        path = os.path.join(self.rules_path, filename)
        try:
            tree = ElementTree.parse(path)
            return tree.getroot()
        except Exception as e:
            logger.warning('parse xml failed ({file})'.format(file=path))
            return None
