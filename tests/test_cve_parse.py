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
import os
import xml.etree.ElementTree as eT
from cobra.cve_parse import CveParse


target_directory = './vulnerabilities/requirements.txt'
rule_path = './examples/cve.xml'
rule_cve_path = '../rules/CVI-999999.xml'
rule_cve_one = '../rules/CVI-999one.xml'


def test_cve_parse():
    cve = CveParse(rule_path, target_directory)
    cve.cve_parse()
    assert 'CVE-2017-5645' in cve.get_result()


def test_cve_info():
    test_info = {}
    cve = CveParse(rule_path, target_directory)
    tree = cve.parse_xml(cve.cve_file)
    root = tree.getroot()
    childs = root.iter('%sentry' % cve.NS)
    for child in childs:  # child is entry Element
        test_info = cve.cve_info(child)
    assert isinstance(test_info, dict)


def test_parse_xml():
    cve = CveParse(rule_path, target_directory)
    tree = cve.parse_xml(cve.cve_file)
    root = eT.parse(rule_path)
    assert isinstance(tree, type(root))


def test_get_result():
    cve = CveParse(rule_path, target_directory)
    cve.cve_parse()
    assert 'CVE-2017-5645' in cve.get_result()


def test_rule_xml():
    cve = CveParse(rule_path, target_directory)
    cve.rule_xml()
    assert os.path.exists(rule_cve_one)
    os.remove(rule_cve_one)


def test_rule_parse():
    cve = CveParse(rule_path, target_directory)
    cve.rule_parse(rule_cve_path)
    assert 'flask vul' in cve.get_rule()


def test_rule_info():
    test_info = {}
    cve = CveParse(rule_path, target_directory)
    tree = cve.parse_xml(rule_cve_path)
    root = tree.getroot()
    cves = root.iter('cve')
    for cvea in cves:
        test_info = cve.rule_info(cvea)
    assert 'cpe' in test_info


def test_get_rule():
    cve = CveParse(rule_path, target_directory)
    cve.rule_parse(rule_cve_path)
    assert 'flask vul' in cve.get_rule()


def test_scan_cve():
    cve = CveParse(rule_path, target_directory)
    cve.scan_cve(rule_cve_path)
    assert 'Flask:0.10.1' in cve.get_scan_result()


def test_get_scan_result():
    cve = CveParse(rule_path, target_directory)
    cve.scan_cve(rule_cve_path)
    assert 'Flask:0.10.1' in cve.get_scan_result()
