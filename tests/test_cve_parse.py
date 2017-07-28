# -*- coding: utf-8 -*-
import unittest
import os
import xml.etree.ElementTree as eT
from cobra.cve_parse import CveParse


class TestCveParse(unittest.TestCase):
    def test_cve_parse(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.cve_parse()
        self.assertTrue('CVE-2017-9994' in cve.get_result())

    def test_cve_info(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        tree = cve.parse_xml(cve.cve_file)
        root = tree.getroot()
        childs = root.iter('%sentry' % cve.NS)
        for child in childs:  # child is entry Element
            cve_info = cve.cve_info(child)
        self.assertTrue('access-complexity' in cve_info)

    def test_parse_xml(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        tree = cve.parse_xml(cve.cve_file)
        root = eT.parse('./examples/cve.xml')
        self.assertIsInstance(tree, type(root))

    def test_get_result(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.cve_parse()
        self.assertTrue('CVE-2017-9994' in cve.get_result())

    def test_rule_xml(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.rule_xml()
        self.assertTrue(os.path.exists(cve.rule_file))

    def test_rule_parse(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.rule_parse()
        self.assertTrue('CVE-2017-9994' in cve.get_rule())

    def test_rule_info(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        tree = cve.parse_xml(cve.rule_file)
        root = tree.getroot()
        cves = root.iter('cve')
        for cvea in cves:
            rule_info = cve.rule_info(cvea)
        self.assertTrue('cpe' in rule_info)

    def test_get_rule(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.rule_parse()
        self.assertTrue('CVE-2017-9994' in cve.get_rule())

    def test_scan_cve(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.scan_cve()
        self.assertTrue('log4j:2.1' in cve.get_scan_result())

    def test_get_scan_result(self):
        cve = CveParse('../tests/examples/cve.xml', '/Users/blbana/Croba/cobra/tests/examples/pom.xml')
        cve.scan_cve()
        self.assertTrue('log4j:2.1' in cve.get_scan_result())