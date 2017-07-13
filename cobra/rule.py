import os
from .config import rules_path
from .log import logger
from xml.etree import ElementTree


def to_bool(value):
    """Converts 'something' to boolean. Raises exception for invalid formats"""
    if str(value).lower() in ("on", "yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in ("off", "no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


class Rule(object):
    def __init__(self):
        self.rules_path = rules_path

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
            l_chiefly = False
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
        """
        Get all rules
        :return:
         [
            {
                'name': "Reflect XSS",
                'vid': '10010',
                'status': True,
                'vulnerability': 'XSS',
                'author': 'Feei <feei@feei.cn>',
                'file': 'reflect.php.xml',
                'test': {
                    'false': [
                        'code test case1',
                        'code test case2'
                    ],
                    'true': [
                        'code test case 1',
                        'code test case 2'
                    ]
                },
                'rule': [
                    'match regex 1',
                    'match regex 2',
                    'repair regex 3'
                ],
                'language': 'php'
            }
         ]
        """
        vulnerabilities = []
        for vulnerability_name in os.listdir(self.rules_path):
            v_path = os.path.join(self.rules_path, vulnerability_name)
            if os.path.isfile(v_path):
                continue
            for rule_filename in os.listdir(v_path):
                v_rule_path = os.path.join(v_path, rule_filename)
                if os.path.isfile(v_rule_path) is not True:
                    continue
                # rule information
                rule_info = {
                    'name': {},
                    'file': rule_filename,
                    'vulnerability': vulnerability_name,
                    'test': {
                        'true': [],
                        'false': []
                    },
                    'language': rule_filename.split('.xml')[0].split('.')[1],
                    'block': '',
                    'repair': '',
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
                        rule_info['name'] = x.get('value')
                    if x.tag == 'status':
                        rule_info['status'] = to_bool(x.get('value'))
                    if x.tag == 'author':
                        name = x.get('name')
                        email = x.get('email')
                        rule_info['author'] = '{name}<{email}>'.format(name=name, email=email)
                    if x.tag in ['match', 'repair']:
                        rule_info[x.tag] = x.text.strip()
                    if x.tag == 'test':
                        for case in x:
                            case_ret = case.get('assert').lower()
                            case_test = case.text.strip()
                            if case_ret in ['true', 'false']:
                                rule_info['test'][case_ret].append(case_test)
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
