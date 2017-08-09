<<<<<<< HEAD
#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cobra
    ~~~~~

    Implements cobra main

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import datetime
import os
import requests
import urllib
import threading
import gzip
import xml.etree.cElementTree as eT
import multiprocessing
from config import project_directory, Config
=======
# -*- coding: utf-8 -*-
import datetime
import xml.etree.ElementTree as eT
>>>>>>> upstream/master
from log import logger
from dependencies import Dependencies


class CveParse(object):
<<<<<<< HEAD
    def __init__(self, target_file, project_path, year=None):
=======
    def __init__(self, target_file, project_path):
>>>>>>> upstream/master
        """
        :param target_file: The cve_file's path
        """
        self.cve_file = target_file
        self.pro_file = project_path
<<<<<<< HEAD
        self.year = year
        self._result = {}  # {'cve_id':{'access-complexity':xxx, 'cpe':[]}} access-complexity and cpe may be None
        self._rule = {}
        self._scan_result = {}
=======
        self._result = {}  # {'cve_id':{'access-complexity':xxx, 'cpe':[]}} access-complexity and cpe may be None
        self._rule = {}
        self._scan_result = {}
        self.rule_file = "../rules/CVI-999999.xml"
        self.rule_files = ["../rules/CVI-999999.xml",
                           "../rules/CVI-Rule.xml"]  # CVI-999999.xml is cve rule, CVI-Rule.xml is custom rule
>>>>>>> upstream/master
        self.CVSS = "{http://scap.nist.gov/schema/cvss-v2/0.2}"
        self.VULN = "{http://scap.nist.gov/schema/vulnerability/0.4}"
        self.NS = "{http://scap.nist.gov/schema/feed/vulnerability/2.0}"

    def cve_parse(self):
        """
        Resolve the latest rules,parse new rule from cve.xml
        :return: None
        """
<<<<<<< HEAD
        cve_file = self.get_cve_file()
        if not isinstance(cve_file, list):
            tree = self.parse_xml(cve_file)
            root = tree.getroot()
            childs = root.iter('%sentry' % self.NS)
            for child in childs:  # child is entry Element
                cve_id = child.attrib['id']
                cve_info = self.cve_info(child)
                if len(cve_info) != 0:
                    self._result[cve_id] = cve_info
        else:
            for filename in cve_file:
                tree = self.parse_xml(filename)
                root = tree.getroot()
                childs = root.iter('%sentry' % self.NS)
                for child in childs:  # child is entry Element
                    cve_id = child.attrib['id']
                    cve_info = self.cve_info(child)
                    if len(cve_info) != 0:
                        self._result[cve_id] = cve_info

    def get_cve_file(self):
        cve_file = []
        if os.path.isfile(self.cve_file):
            return self.cve_file
        else:
            for root, dirs, filenames in os.walk(self.cve_file):
                for filename in filenames:
                    cve_file.append(os.path.join(root, filename))
            return cve_file
=======
        tree = self.parse_xml(self.cve_file)
        root = tree.getroot()
        childs = root.iter('%sentry' % self.NS)
        for child in childs:  # child is entry Element
            cve_id = child.attrib['id']
            cve_info = self.cve_info(child)
            self._result[cve_id] = cve_info
>>>>>>> upstream/master

    def cve_info(self, entry):
        """
        :param entry: every entry Element
        :return:Information inside each entry node
        """
        cpe_list = []
        cve_info = {}
<<<<<<< HEAD
        black_lists = ['ffmpeg', 'linux', 'ie', 'apple_tv', 'iphone_os', 'watchos', 'mac_os_x', 'windows', 'ios',
                       'android', 'flash_player', 'office', 'wireshark', 'safari', 'mysql', 'word', '.net_framework',
                       'samba', 'ntp', 'tomcat', 'unixware', 'vpn', 'netware', 'proxy_server', 'http_server', 'irix',
                       'solaris', 'weblogic_server', 'kde', 'dhcpd', 'database_server', 'mandrake_linux', 'openssl'
                                                                                                          'suse_linux',
                       'vim', 'debian_linux', 'putty', 'ubuntu_linux', 'mozilla', 'ftp_server', 'cvs'
                                                                                                'oracle',
                       'ws_ftp_server', 'surgemail', 'opera_web_browser', 'sql_server', 'ethereal', 'gaim',
                       'wu-ftpd', 'cluster_server', 'catos', 'mantis', 'quicktime', 'security_linux', 'firefox',
                       'jetty_http_server', 'php:', 'enterprise_linux', 'oracle10g', 'oracle9g', 'oracle8g', 'firehol',
                       'fetchmail', 'postgresql', 'freebsd', 'chrome']
        products = entry.iter('%sproduct' % self.VULN)
=======
        products = entry.iter('%sproduct' % self.VULN)
        access_complexity = entry.find('.//%saccess-complexity' % self.CVSS)
        summary = entry.find('.//%ssummary' % self.VULN)
>>>>>>> upstream/master
        for product in products:
            module_version = product.text.split(':')
            if len(module_version) > 4:
                module_ = module_version[3] + ':' + module_version[4]
<<<<<<< HEAD
            elif len(module_version) == 4:
                module_ = module_version[3]
            else:
                module_ = module_version[2]
            for black_list in black_lists:
                if str(module_).startswith(black_list):
                    return cve_info
            cpe_list.append(module_)
            cve_info['cpe'] = cpe_list
=======
            else:
                module_ = module_version[3]
            cpe_list.append(module_)
            cve_info['cpe'] = cpe_list
        if access_complexity is None:
            cve_info['access-complexity'] = 'unknown'
        else:
            cve_info['access-complexity'] = access_complexity.text
        if summary is None:
            cve_info['summary'] = 'unknown'
        else:
            cve_info['summary'] = summary.text
>>>>>>> upstream/master
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
<<<<<<< HEAD
        logger.info('The rule CVE-999' + str(self.year)[1:] + '.xml are being updated. Please wait for a moment....')
=======
        logger.info('The rules are being updated. Please wait for a moment....')
>>>>>>> upstream/master
        self.cve_parse()
        cobra = eT.Element('cobra')  # root Ele
        cobra.set('document', 'https://github.com/wufeifei/cobra')
        for cve_id in self._result.keys():
            cve_child = eT.Element('cve')  # cve Ele
            cve_child.set('id', cve_id)
<<<<<<< HEAD
            # products = eT.Element('products')
=======
            if 'access-complexity' in self._result[cve_id]:
                level = eT.Element('level')
                level.text = self._result[cve_id]['access-complexity']
                cve_child.append(level)  # level in cve
            products = eT.Element('products')
>>>>>>> upstream/master
            if 'cpe' in self._result[cve_id]:
                for product_ in self._result[cve_id]['cpe']:
                    product = eT.Element('product')
                    product.text = product_
<<<<<<< HEAD
                    cve_child.append(product)  # product in products
                    # cve_child.append(products)  # products in cve
            cobra.append(cve_child)  # cve in cobra
        self.pretty(cobra)
        tree = eT.ElementTree(cobra)
        tree.write('../rules/CVI-999' + str(self.year)[1:] + '.xml')
        endtime = datetime.datetime.now()
        logger.info('CVE-999' + str(self.year)[1:] + '.xml Rule update succeeds, times:%ds' % (endtime - starttime).seconds)
=======
                    products.append(product)  # product in products
                cve_child.append(products)  # products in cve
            if 'summary' in self._result[cve_id]:
                summary = eT.Element('summary')
                summary.text = self._result[cve_id]['summary']
                cve_child.append(summary)
            cobra.append(cve_child)  # cve in cobra
        self.pretty(cobra)
        tree = eT.ElementTree(cobra)
        tree.write(self.rule_file)
        endtime = datetime.datetime.now()
        logger.info('Rule update succeeds, times:%ds' % (endtime - starttime).seconds)
>>>>>>> upstream/master

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

<<<<<<< HEAD
    def rule_parse(self, file_):
        """
        :return: rules from CVI-999999.xml and CVI-999999.xml
        """
        tree = self.parse_xml(file_)
        root = tree.getroot()
        cves = root.iter('cve')
        for cve_child in cves:
            cve_id = cve_child.attrib['id']
            rule_info = self.rule_info(cve_child)
            self._rule[cve_id] = rule_info
=======
    def rule_parse(self):
        """
        :return: rules from CVI-Rule.xml and CVI-999999.xml
        """
        for rule_file in self.rule_files:
            tree = self.parse_xml(rule_file)
            root = tree.getroot()
            cves = root.iter('cve')
            for cve_child in cves:
                cve_id = cve_child.attrib['id']
                rule_info = self.rule_info(cve_child)
                self._rule[cve_id] = rule_info
>>>>>>> upstream/master

    @staticmethod
    def rule_info(cve_child):
        rule_info = {}
        cpe_list = []
<<<<<<< HEAD
=======
        level = cve_child.find('.//level')
        rule_info['level'] = level.text
>>>>>>> upstream/master
        products = cve_child.iter('product')
        for product in products:
            cpe_list.append(product.text)
        rule_info['cpe'] = cpe_list
<<<<<<< HEAD
=======
        summary = cve_child.find('.//summary')
        rule_info['summary'] = summary.text
>>>>>>> upstream/master
        return rule_info

    def get_rule(self):
        """
<<<<<<< HEAD
        :return: The rule from CVI-999999.xml and CVI-999999.xml
        """
        return self._rule

    def scan_cve(self, file_):
        """
        :return:Analytical dependency，Match the rules and get the result
        """
        self.rule_parse(file_)
=======
        :return: The rule from CVI-999999.xml and CVI-Rule.xml
        """
        return self._rule

    def scan_cve(self):
        """
        :return:Analytical dependency，Match the rules and get the result
        """
        self.rule_parse()
>>>>>>> upstream/master
        cve = self.get_rule()
        dependency = Dependencies(self.pro_file)
        project_info = dependency.get_result
        for pro_info in project_info:
            module_version = pro_info + ':' + project_info[pro_info]
            self.set_scan_result(cve, module_version)
        self.log_result()

    def set_scan_result(self, cves, module_version):
        """
        :param cves:
        :param module_version:
        :return:set the scan result
        """
<<<<<<< HEAD
        scan_cves = []
        for cve_child in cves:
            if module_version in cves[cve_child]['cpe']:
                scan_cves.append(cve_child)
=======
        scan_cves = {}
        for cve_child in cves:
            if module_version in cves[cve_child]['cpe']:
                scan_cves[cve_child] = cves[cve_child]['level']
>>>>>>> upstream/master
        if len(scan_cves):
            self._scan_result[module_version] = scan_cves

    def log_result(self):
        for module_ in self._scan_result:
            for cve_child in self._scan_result[module_]:
                cve_id = cve_child
<<<<<<< HEAD
                logger.warning('Find the module ' + module_ + ' have ' + cve_id)
=======
                cve_level = self._scan_result[module_][cve_child]
                logger.warning('Find the module ' + module_ + ' have ' + cve_id + ' and level is ' + cve_level)
>>>>>>> upstream/master
            count = len(self._scan_result[module_])
            logger.warning('The ' + module_ + ' module have ' + str(count) + ' CVE Vul')

    def get_scan_result(self):
        return self._scan_result
<<<<<<< HEAD


def rule_parse():
    if is_update():
        gz_files = download_rule_gz()
        un_gz(gz_files)
        pool = multiprocessing.Pool(processes=100)
        for year in range(2002, datetime.datetime.now().year+1):
            cve_xml = "../rules/%d.xml" % year
            pool.apply_async(rule_single, args=(cve_xml, year))
        pool.close()
        pool.join()
        for year in range(2002, datetime.datetime.now().year+1):
            os.remove("../rules/%d.xml" % year)
        logger.info("The rule update success, start scan cve vuls")
    else:
        logger.info("The CVE Rule not update, start scan cve vuls")


def download_rule_gz():
    threads = []
    files = []
    start_time = datetime.datetime.now()
    for year in range(2002, datetime.datetime.now().year+1):
        url = "https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-" + str(year) + ".xml.gz"
        logger.info("start download " + str(year) + ".xml.gz")
        thread = threading.Thread(target=urllib.urlretrieve, args=(url, "../rules/"+str(year)+".xml.gz"))
        thread.start()
        threads.append(thread)
        logger.info('CVE-' + str(year) + " is download success")
        files.append(os.path.join(project_directory, "rules/" + str(year) + ".xml.gz"))
    for t in threads:
        t.join()
    end_time = datetime.datetime.now()
    logger.info("All CVE xml file already download success, use time:%ds" % (end_time-start_time).seconds)
    return files


def un_gz(gz_files):
    """ungz zip file"""
    start_time = datetime.datetime.now()
    logger.info("Start decompress rule files, Please wait a moment....")
    for gz_file in gz_files:
        f_name = gz_file.replace(".gz", "")
        g_file = gzip.GzipFile(gz_file)
        open(f_name, "w+").write(g_file.read())
        g_file.close()
        os.remove(gz_file)
    end_time = datetime.datetime.now()
    logger.info("Decompress success, use time:%ds" % (end_time-start_time).seconds)


def rule_single(target_directory, year):
    CveParse(target_directory, '.', year).rule_xml()


def is_update():
    url = "https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-modified.meta"
    r = requests.get(url)
    index = r.text.find('sha256:')
    sha256_now = r.text[index+7:].strip()
    sha256_local = Config(level1='cve', level2='modified').value
    if sha256_local != sha256_now:
        logger.info("The CVE Rule already update, start update local rule")
        return True


def scan(target_directory):
    cve_files = []
    rule_path = os.path.join(project_directory, 'rules')
    files = os.listdir(rule_path)
    for cvi_file in files:
        if cvi_file.startswith('CVI-999'):
            cve_files.append(cvi_file)
    pool = multiprocessing.Pool(processes=50)
    for cve_file in cve_files:
        cve_path = os.path.join(rule_path, cve_file)
        pool.apply_async(scan_single, args=(target_directory, cve_path))
    pool.close()
    pool.join()


def scan_single(target_directory, cve_path):
    CveParse('.', target_directory).scan_cve(cve_path)
=======
>>>>>>> upstream/master
