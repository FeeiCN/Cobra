# -*- coding: utf-8 -*-

"""
    tests.config
    ~~~~~~~~~~~~

    Tests utils.config

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from cobra.utils.config import Config


def test_read_exception():
    value = Config('test', 'test').value
    assert value is None


def test_read():
    pass


def test_copy():
    pass


def test_initialize():
    pass


def test_read_normal():
    value = Config('upload', 'extensions').value
    assert 'rar' in value


def test_read_rules():
    rules = Config().rule()
    assert 'name' in rules
    assert 'url' in rules
    assert 'submit' in rules
    # vulnerabilities
    assert 'vulnerabilities' in rules
    assert 'XSS' in rules['vulnerabilities']
    # -- name
    assert 'name' in rules['vulnerabilities']['XSS']
    # -- rules
    assert 'rules' in rules['vulnerabilities']['XSS']
    assert 'en' in rules['vulnerabilities']['XSS']['name']
    assert 'cn' in rules['vulnerabilities']['XSS']['name']
    assert 'name' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'description' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'en' in rules['vulnerabilities']['XSS']['rules'][0]['description']
    assert 'cn' in rules['vulnerabilities']['XSS']['rules'][0]['description']
    assert 'author' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'creator' in rules['vulnerabilities']['XSS']['rules'][0]['author']
    assert 'language' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'match' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'repair' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'level' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'status' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'test' in rules['vulnerabilities']['XSS']['rules'][0]
    assert 'code' in rules['vulnerabilities']['XSS']['rules'][0]
    # languages
    assert 'languages' in rules
    assert 'PHP' in rules['languages']
    assert 'extensions' in rules['languages']['PHP']
    assert 'frameworks' in rules['languages']['PHP']
    assert 'name' in rules['languages']['PHP']['frameworks'][0]
    assert 'code' in rules['languages']['PHP']['frameworks'][0]
    assert 'rule' in rules['languages']['PHP']['frameworks'][0]
    assert 'file' in rules['languages']['PHP']['frameworks'][0]['rule']
    assert 'folder' in rules['languages']['PHP']['frameworks'][0]['rule']
