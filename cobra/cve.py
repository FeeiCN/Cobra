# -*- coding: utf-8 -*-

"""
    CVE
    ~~~

    Implements CVE Rules Parser

    :author:    BlBana <635373043@qq.com>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import datetime
import gzip
import multiprocessing
import os
import subprocess
import threading
import xml.etree.cElementTree as eT

import requests

from .config import project_directory, Config, config_path
from .dependencies import Dependencies, Comparator
from .log import logger
from .result import VulnerabilityResult

try:
    from urllib import urlretrieve  # Python2
except ImportError:
    from urllib.request import urlretrieve  # Python3

try:
    from configparser import ConfigParser
except ImportError:
    from ConfigParser import ConfigParser


class CveParse(object):
    def __init__(self, target_file, project_path, year=None):
        """
        :param target_file: The cve_file's path
        """
        self.cve_file = target_file
        self.pro_file = project_path
        self.year = year
        self._result = {}  # {'cve_id':{'access-complexity':xxx, 'cpe':[]}} access-complexity and cpe may be None
        self._rule = {}
        self._scan_result = {}
        self.res = True
        self.CVSS = "{http://scap.nist.gov/schema/cvss-v2/0.2}"
        self.VULN = "{http://scap.nist.gov/schema/vulnerability/0.4}"
        self.NS = "{http://scap.nist.gov/schema/feed/vulnerability/2.0}"

    def cve_parse(self):
        """
        Resolve the latest rules,parse new rule from cve.xml
        :return: None
        """
        cve_file = self.get_cve_file()
        if not isinstance(cve_file, list):
            tree = self.parse_xml(cve_file)
            root = tree.getroot()
            childs = root.findall('.//%sentry' % self.NS)
            for child in childs:  # child is entry Element
                cve_id = child.attrib['id']
                cve_info = self.cve_info(child)
                if len(cve_info) != 0:
                    self._result[cve_id] = cve_info
        else:
            for filename in cve_file:
                tree = self.parse_xml(filename)
                root = tree.getroot()
                childs = root.findall('.//%sentry' % self.NS)
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

    def cve_info(self, entry):
        """
        :param entry: every entry Element
        :return:Information inside each entry node
        """
        cpe_list = []
        cve_info = {}
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
        products = entry.findall('.//%sproduct' % self.VULN)
        access_complexity = entry.find('.//%saccess-complexity' % self.CVSS)
        for product in products:
            module_version = product.text.split(':')
            if len(module_version) > 4:
                module_ = module_version[3] + ':' + module_version[4]
            elif len(module_version) == 4:
                module_ = module_version[3]
            else:
                module_ = module_version[2]
            for black_list in black_lists:
                if str(module_).startswith(black_list):
                    cve_info = {}
                    return cve_info
            cpe_list.append(module_)
        if len(cpe_list) == 0:
            return cve_info
        else:
            cve_info['cpe'] = cpe_list

        if access_complexity is None:
            cve_info['level'] = 'unknown'
        else:
            cve_info['level'] = access_complexity.text
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
        logger.info('The rule CVE-999' + str(self.year)[1:] + '.xml are being updated. Please wait for a moment....')
        self.cve_parse()
        cobra = eT.Element('cobra')  # root Ele
        cobra.set('document', 'https://github.com/WhaleShark-Team/cobra')
        for cve_id in self._result.keys():
            cve_child = eT.Element('cve')  # cve Ele
            cve_child.set('id', cve_id)
            cve_child.set('level', self._result[cve_id]['level'])
            if 'cpe' in self._result[cve_id]:
                for product_ in self._result[cve_id]['cpe']:
                    product = eT.Element('product')
                    product.text = product_
                    cve_child.append(product)  # product in products
            cobra.append(cve_child)  # cve in cobra
        self.pretty(cobra)
        tree = eT.ElementTree(cobra)
        rule_path = project_directory + '/rules/CVI-999'
        tree.write(rule_path + str(self.year)[1:] + '.xml')
        endtime = datetime.datetime.now()
        logger.info(
            'CVE-999' + str(self.year)[1:] + '.xml Rule update succeeds, times:%ds' % (endtime - starttime).seconds)

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

    def rule_parse(self, file_):
        """
        :return: rules from CVI-999999.xml and CVI-999999.xml
        """
        tree = self.parse_xml(file_)
        root = tree.getroot()
        cves = root.findall('.//cve')
        for cve_child in cves:
            cve_id = cve_child.attrib['id']
            cve_level = cve_child.attrib['level']
            rule_info = self.rule_info(cve_child)
            rule_info['level'] = cve_level
            self._rule[cve_id] = rule_info

    @staticmethod
    def rule_info(cve_child):
        rule_info = {}
        cpe_list = []
        products = cve_child.findall('.//product')
        for product in products:
            cpe_list.append(
                {
                    'name': product.text.lower().split(':')[0],
                    'version': product.text.lower().split(':')[1],
                }
            )
        rule_info['cpe'] = cpe_list
        return rule_info

    def get_rule(self):
        """
        :return: The rule from CVI-999999.xml and CVI-999999.xml
        """
        return self._rule

    def scan_cve(self, file_):
        """
        :return:Analytical dependency，Match the rules and get the result
        """
        self.rule_parse(file_)
        cve = self.get_rule()
        dependency = Dependencies(self.pro_file)
        project_info = dependency.get_result
        for pro_info in project_info:
            module_version = {
                'name': pro_info.lower(),
                'version': project_info.get(pro_info).get('version'),
                'format': project_info.get(pro_info).get('format'),
            }
            self.set_scan_result(cve, module_version)
        self.log_result()

    def set_scan_result(self, cves, module_version):
        """
        :param cves:
        :param module_version: {"name": "flask", "version": "==0.10.1", "format": "python"}
        :return:set the scan result
        """
        scan_cves = {}
        for cve_child in cves:
            for v in cves[cve_child]['cpe']:
                if module_version.get('name') == v.get('name'):
                    comparator = Comparator(rule_version=v.get('version'), dep_version=module_version.get('version'), fmt=module_version.get('format'))
                    if comparator.compare():
                        scan_cves[cve_child] = cves[cve_child]['level']
        if len(scan_cves):
            self._scan_result[module_version.get('name') + ':' + module_version.get('version')] = scan_cves

    def log_result(self):
        for module_ in self._scan_result:
            for cve_child in self._scan_result[module_]:
                cve_id = cve_child
                level = self._scan_result[module_][cve_id]
                logger.debug('Find the module ' + module_ + ' have ' + cve_id + ',level: ' + level)
            count = len(self._scan_result[module_])
            logger.debug('The ' + module_ + ' module have ' + str(count) + ' CVE Vul(s)')

    def get_scan_result(self):
        return self._scan_result


def rule_parse():
    if is_update():
        gz_files = download_rule_gz()
        un_gz(gz_files)
        pool = multiprocessing.Pool()
        for year in range(2002, datetime.datetime.now().year + 1):
            cve_xml = project_directory + "/rules/%d.xml" % year
            pool.apply_async(rule_single, args=(cve_xml, year))
        pool.close()
        pool.join()
        for year in range(2002, datetime.datetime.now().year + 1):
            os.remove(project_directory + "/rules/%d.xml" % year)
        logger.info("The rule update success, start scan cve vuls")
        return True
    else:
        logger.info("The CVE Rule not update, start scan cve vuls")


def download_rule_gz():
    threads = []
    files = []
    start_time = datetime.datetime.now()
    for year in range(2002, datetime.datetime.now().year + 1):
        url = "https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-" + str(year) + ".xml.gz"
        logger.info("start download " + str(year) + ".xml.gz")
        thread = threading.Thread(target=urlretrieve,
                                  args=(url, project_directory + "/rules/" + str(year) + ".xml.gz"))
        thread.start()
        threads.append(thread)
        files.append(project_directory + "/rules/" + str(year) + ".xml.gz")
    for t in threads:
        t.join()
    end_time = datetime.datetime.now()
    for afile in files:
        param = ['file', afile]
        p = subprocess.Popen(param, shell=False, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        res_out, res_err = p.communicate()

        res_out = res_out.decode('utf-8')
        res_err = res_err.decode('utf-8')

        if 'HTML' in res_out:
            os.remove(afile)
            afile_name = os.path.split(afile)[1]
            year = afile_name.split('.')[0]
            url = "https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-" + str(year) + ".xml.gz"
            try:
                urlretrieve(url, afile)
            except IOError:
                logger.warning('[CVE] The {} download fail'.format(afile))

    logger.info("All CVE xml file already download success, use time:%ds" % (end_time - start_time).seconds)
    return files


def un_gz(gz_files):
    """ungz zip file"""
    start_time = datetime.datetime.now()
    logger.info("Start decompress rule files, Please wait a moment....")
    for gz_file in gz_files:
        if os.path.exists(gz_file):
            f_name = gz_file.replace(".gz", "")

            try:
                g_file = gzip.GzipFile(gz_file, "rb")
                open(f_name, "wb+").write(g_file.read())
                g_file.close()
            except IOError:
                logger.warning('[CVE] The {} download fail'.format(gz_file))

            os.remove(gz_file)
    end_time = datetime.datetime.now()
    logger.info("Decompress success, use time:%ds" % (end_time - start_time).seconds)
    return True


def rule_single(target_directory, year):
    CveParse(target_directory, '.', year).rule_xml()


def is_update():
    url = "https://static.nvd.nist.gov/feeds/xml/cve/2.0/nvdcve-2.0-modified.meta"
    requests.packages.urllib3.disable_warnings()
    r = requests.get(url, verify=False)
    index = r.text.find('sha256:')
    sha256_now = r.text[index + 7:].strip()
    sha256_local = Config(level1='cve', level2='modified').value
    if sha256_local != sha256_now:
        logger.info("The CVE Rule already update, start update local rule")
        config = ConfigParser()
        config.read(config_path)
        config.set('cve', 'modified', sha256_now)
        try:
            fi = open(config_path, 'w')
            config.write(fi)
            fi.close()
        except IOError as e:
            logger.warning(e)
        logger.info("The sha256 been update")
        return True
    return False


def scan_cve(target_directory, specific_rule=None):
    cve_vuls = []
    cve_files = []

    def store(results):
        if len(results[0]) != 0:
            for module_ in results[0]:
                for cve_id, cve_level in results[0][module_].items():
                    cve_path = results[1]
                    cve_vul = parse_match(cve_path, cve_id, cve_level, module_, target_directory)
                    cve_vuls.append(cve_vul)
        else:
            logger.debug('[SCAN] [STORE] Not found vulnerabilities on this rule!')

    rule_path = os.path.join(project_directory, 'rules')
    files = os.listdir(rule_path)
    if specific_rule:
        if specific_rule in files:
            cve_files.append(specific_rule)
    else:
        for cvi_file in files:
            if cvi_file.startswith('CVI-999'):
                cve_files.append(cvi_file)
    if len(cve_files) == 0:
        logger.info("Can't find the rules, please update rules")
        return
    try:
        pool = multiprocessing.Pool()
    except IOError:
        logger.warning('[SCAN] [CVE] IOError Broken pipe')
    logger.info('[PUSH] {rc} CVE Rules'.format(rc=len(cve_files)))
    for cve_file in cve_files:
        cve_path = os.path.join(rule_path, cve_file)
        pool.apply_async(scan_single, args=(target_directory, cve_path), callback=store)
    pool.close()
    pool.join()
    return cve_vuls


def scan_single(target_directory, cve_path):
    """
    :param target_directory: scan path
    :param cve_path: CVI-999***.xml
    :return:
    """
    cve = CveParse('.', target_directory)
    cve.scan_cve(cve_path)
    return cve.get_scan_result(), cve_path


def parse_match(cve_path, cve_id, cve_level, module_, target_directory):
    flag = 0
    file_path = 'unkown'
    mr = VulnerabilityResult()
    module_name, module_version = module_.split(':')
    cvi = cve_path.lower().split('cvi-')[1][:6]
    if cve_level == 'LOW':
        cve_level = 2

    elif cve_level == 'MEDIUM':
        cve_level = 5

    elif cve_level == 'HIGH':
        cve_level = 8

    for root, dirs, filenames in os.walk(target_directory):
        for filename in filenames:
            if filename == 'pom.xml' and flag != 2:
                file_path = os.path.join(root, filename)
                file_path = file_path.replace(target_directory, '')
                flag = 1

            elif filename == 'requirements.txt' and flag != 1:
                file_path = os.path.join(root, filename)
                file_path = file_path.replace(target_directory, '')
                flag = 2

            elif file_path == 'package.json':
                file_path = os.path.join(root, filename)
                file_path = file_path.replace(target_directory, '')

    if flag != 0:
        mr.file_path = file_path

    else:
        mr.file_path = 'unkown'
    mr.language = '*'
    mr.id = cvi
    mr.rule_name = '引用了存在漏洞的三方组件'
    mr.level = cve_level
    mr.line_number = 1
    mr.analysis = 'Dependencies Matched(依赖匹配)'
    mr.code_content = module_name + ':' + module_version
    mr.solution = """
        三方依赖**""" + module_name + """:""" + module_version + """**存在CVE漏洞，CVE漏洞编号为: **""" + cve_id + """**
        ## 安全风险
        
        ## 安全修复
        请根据对应厂商公告，及时更新三方依赖至安全版本
    """

    logger.debug('[CVE {i}] {r}:Find {n}:{v} have vul {c} and level is {l}'.format(i=mr.id, r=mr.rule_name,
                                                                                   n=mr.file_path, v=mr.line_number,
                                                                                   c=mr.language, l=mr.level))

    return mr
