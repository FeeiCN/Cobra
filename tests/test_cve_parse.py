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
=======
# -*- coding: utf-8 -*-
>>>>>>> upstream/master
import os
import xml.etree.ElementTree as eT
from cobra.cve_parse import CveParse


def test_cve_parse():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.cve_parse()
    assert 'CVE-2017-9994' in cve.get_result()


def test_cve_info():
    test_info = {}
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    tree = cve.parse_xml(cve.cve_file)
    root = tree.getroot()
    childs = root.iter('%sentry' % cve.NS)
    for child in childs:  # child is entry Element
        test_info = cve.cve_info(child)
    assert 'access-complexity' in test_info


def test_parse_xml():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    tree = cve.parse_xml(cve.cve_file)
    root = eT.parse('./examples/cve.xml')
    assert isinstance(tree, type(root))


def test_get_result():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.cve_parse()
    assert 'CVE-2017-9994' in cve.get_result()


def test_rule_xml():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.rule_xml()
    assert os.path.exists(cve.rule_file)


def test_rule_parse():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.rule_parse()
    assert 'CVE-2017-9994' in cve.get_rule()


def test_rule_info():
    test_info = {}
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    tree = cve.parse_xml(cve.rule_file)
    root = tree.getroot()
    cves = root.iter('cve')
    for cvea in cves:
        test_info = cve.rule_info(cvea)
    assert 'cpe' in test_info


def test_get_rule():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.rule_parse()
    assert 'CVE-2017-9994' in cve.get_rule()


def test_scan_cve():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.scan_cve()
    assert 'log4j:2.1' in cve.get_scan_result()


def test_get_scan_result():
    cve = CveParse('../tests/examples/cve.xml', './examples/pom.xml')
    cve.scan_cve()
    assert 'log4j:2.1' in cve.get_scan_result()
