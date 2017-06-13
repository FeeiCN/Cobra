import os
from cobra.utils.config import rules_path
from cobra.utils.log import logger
from cobra.utils.common import to_bool
from xml.etree import ElementTree


class Rules(object):
    def __init__(self):
        self.rules_path = rules_path

    @property
    def languages(self):
        """
        Read all language extensions
        :return:
        """
        language_extensions = {}
        xml_languages = self._read_xml('languages.xml')
        if xml_languages is None:
            logger.critical('languages read failed!!!')
            return None
        for language in xml_languages:
            l_name = language.get('name').lower()
            language_extensions[l_name] = []
            for lang in language:
                l_ext = lang.get('value').lower()
                language_extensions[l_name].append(l_ext)
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
            v_name = vulnerability.get('name').lower()
            v_level = int(vulnerability.get('level'))
            v_description = vulnerability[0].text.strip()
            v_repair = vulnerability[1].text.strip()
            vulnerabilities_info[str(v_id)] = {
                'name': v_name,
                'description': v_description,
                'level': v_level,
                'repair': v_repair,
            }
        return vulnerabilities_info

    @property
    def rules(self):
        vulnerabilities = {}
        for vulnerability_name in os.listdir(self.rules_path):
            v_path = os.path.join(self.rules_path, vulnerability_name)
            if os.path.isfile(v_path):
                continue
            vulnerabilities[vulnerability_name] = []
            for rule_filename in os.listdir(v_path):
                v_rule_path = os.path.join(v_path, rule_filename)
                if os.path.isfile(v_rule_path) is not True:
                    continue
                # rule information
                rule_info = {
                    'file': rule_filename,
                    'test': {
                        'true': [],
                        'false': []
                    }
                }
                rule_path = os.path.join(vulnerability_name, rule_filename)
                xml_rule = self._read_xml(rule_path)
                if xml_rule is None:
                    logger.critical('rule read failed!!! ({file})'.format(file=rule_path))
                    continue
                for x in xml_rule:
                    if x.tag == 'vid':
                        rule_info['vid'] = x.get('value')
                    if x.tag == 'name':
                        lang = x.get('lang').lower()
                        rule_info['name'] = {lang: x.text}
                    if x.tag == 'status':
                        rule_info['status'] = to_bool(x.get('value'))
                    if x.tag == 'author':
                        name = x.get('name')
                        email = x.get('email')
                        rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
                    if x.tag in ['match', 'repair']:
                        rule_info[x.tag] = x.text
                    if x.tag == 'test':
                        for case in x:
                            case_ret = case.get('assert').lower()
                            case_test = case.text
                            if case_ret in ['true', 'false']:
                                rule_info['test'][case_ret].append(case_test)
                vulnerabilities[vulnerability_name].append(rule_info)
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
