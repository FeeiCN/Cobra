# -*- coding: utf-8 -*-
import datetime
import xml.etree.ElementTree as eT
from log import logger
from dependencies import Dependencies


class CveParse(object):
    def __init__(self, target_file, project_path):
        """
        :param target_file: The cve_file's path
        """
        self.cve_file = target_file
        self.pro_file = project_path
        self._result = {}  # {'cve_id':{'access-complexity':xxx, 'cpe':[]}} access-complexity and cpe may be None
        self._rule = {}
        self._scan_result = {}
        self.rule_file = "../rules/CVE_Rule.xml"
        self.CVSS = "{http://scap.nist.gov/schema/cvss-v2/0.2}"
        self.VULN = "{http://scap.nist.gov/schema/vulnerability/0.4}"
        self.NS = "{http://scap.nist.gov/schema/feed/vulnerability/2.0}"

    def cve_parse(self):
        """
        Resolve the latest rules,parse new rule from cve.xml
        :return: None
        """
        tree = self.parse_xml(self.cve_file)
        root = tree.getroot()
        childs = root.iter('%sentry' % self.NS)
        for child in childs:  # child is entry Element
            cve_id = child.attrib['id']
            cve_info = self.cve_info(child)
            self._result[cve_id] = cve_info

    def cve_info(self, entry):
        """
        :param entry: every entry Element
        :return:Information inside each entry node
        """
        cpe_list = []
        cve_info = {}
        products = entry.iter('%sproduct' % self.VULN)
        access_complexity = entry.find('.//%saccess-complexity' % self.CVSS)
        for product in products:
            module_version = product.text.split(':')
            if len(module_version) > 4:
                module_ = module_version[3]+':'+module_version[4]
            else:
                module_ = module_version[3]
            cpe_list.append(module_)
            cve_info['cpe'] = cpe_list
        if access_complexity is None:
            cve_info['access-complexity'] = 'unknown'
        else:
            cve_info['access-complexity'] = access_complexity.text
        return cve_info

    @staticmethod
    def parse_xml(file_path):
        return eT.parse(file_path)

    def get_result(self):
        """
        :return:The result from cve.xml,this is new rule
        """
        return self._result

    def rule_xml(self):
        """
        If you want to update rule, Please use this function, it will auto parse rule, and write in file
        :return:
        """
        starttime = datetime.datetime.now()
        logger.info('The rules are being updated. Please wait for a moment....')
        self.cve_parse()
        cobra = eT.Element('cobra')  # root Ele
        cobra.set('document', 'https://github.com/wufeifei/cobra')
        for cve_id in self._result.keys():
            cve = eT.Element('cve')  # cve Ele
            cve.set('id', cve_id)
            if 'access-complexity' in self._result[cve_id]:
                level = eT.Element('level')
                level.text = self._result[cve_id]['access-complexity']
                cve.append(level)  # level in cve
            products = eT.Element('products')
            if 'cpe' in self._result[cve_id]:
                for product_ in self._result[cve_id]['cpe']:
                    product = eT.Element('product')
                    product.text = product_
                    products.append(product)  # product in products
                cve.append(products)  # products in cve
            cobra.append(cve)  # cve in cobra
        self.pretty(cobra)
        tree = eT.ElementTree(cobra)
        tree.write(self.rule_file)
        endtime = datetime.datetime.now()
        logger.info('Rule update succeeds, times:%ds' % (endtime - starttime).seconds)

    def pretty(self, e, level=0):
        """
        :param e:The root Element
        :param level:
        :return: None,pretty the xml file
        """
        if len(e) > 0:
            e.text = '\n' + '\t' * (level + 1)
            for child in e:
                self.pretty(child, level + 1)
            child.tail = child.tail[:-1]
        e.tail = '\n' + '\t' * level

    def rule_parse(self):
        """
        :return: rules from cve_rule.xml
        """
        tree = self.parse_xml(self.rule_file)
        root = tree.getroot()
        cves = root.iter('cve')
        for cve in cves:
            cve_id = cve.attrib['id']
            rule_info = self.rule_info(cve)
            self._rule[cve_id] = rule_info

    @staticmethod
    def rule_info(cve):
        rule_info = {}
        cpe_list = []
        level = cve.find('.//level')
        rule_info['level'] = level.text
        products = cve.iter('product')
        for product in products:
            cpe_list.append(product.text)
        rule_info['cpe'] = cpe_list
        return rule_info

    def get_rule(self):
        return self._rule

    def scan_cve(self):
        self.rule_parse()
        cves = self.get_rule()
        dependeny = Dependencies(self.pro_file)
        pro_infos = dependeny.get_result
        for pro_info in pro_infos:
            module_version = pro_info+':'+pro_infos[pro_info]
            scan_cves = {}
            for cve in cves:
                if module_version in cves[cve]['cpe']:
                    scan_cves[cve] = cves[cve]['level']
            if len(scan_cves):
                self._scan_result[module_version] = scan_cves
        self.log_result()

    def log_result(self):
        for module_ in self._scan_result:
            for cve in self._scan_result[module_]:
                cve_id = cve
                cve_level = self._scan_result[module_][cve]
                logger.warning('Find the module ' + module_ + ' have ' + cve_id + ' and level is ' + cve_level)
            count = len(self._scan_result[module_])
            logger.warning('The ' + module_ + ' module have ' + str(count) + ' CVE Vul')

    def get_scan_result(self):
        return self._scan_result

# a = CveParse('/Users/blbana/Downloads/CVE漏洞/nvdcve-2.0-2017.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
a = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
a.rule_xml()
a.scan_cve()
