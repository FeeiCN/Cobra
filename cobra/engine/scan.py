# -*- coding: utf-8 -*-

"""
    engine.scan
    ~~~~~~~~~~~

    Implements scan

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import multiprocessing
from cobra.engine.sr import SingleRule
from cobra.engine.rules import Rules
from cobra.utils.log import logger

r = Rules()
vulnerabilities = r.vulnerabilities
languages = r.languages
frameworks = r.frameworks
rules = r.rules

"""
{
    'hcp': {
        'rule1': [vr1, vr2]
    },
    'xss': {
        'rule2': [vr3, vr4]
    }
}
"""
find_vulnerabilities = []


def scan_single(target_directory, single_rule):
    return SingleRule(target_directory, single_rule).process()


def store(result):
    find_vulnerabilities.append(result)


def scan(target_directory):
    pool = multiprocessing.Pool()
    if len(rules) == 0:
        logger.critical('no rules!')
        return False
    for idx, single_rule in enumerate(rules):
        # SR(Single Rule)
        logger.info("""Push Rule
                     > index: {idx}
                     > name: {name}
                     > status: {status}
                     > language: {language}
                     > vid: {vid}""".format(
            idx=idx,
            name=single_rule['name']['en'],
            status=single_rule['status'],
            language=single_rule['language'],
            vid=single_rule['vid'],
            match=single_rule['match']
        ))
        if single_rule['status'] is False:
            logger.info('rule disabled, continue...')
            continue
        if single_rule['language'] in languages:
            single_rule['extensions'] = languages[single_rule['language']]
            pool.apply_async(scan_single, args=(target_directory, single_rule), callback=store)
        else:
            logger.critical('unset language, continue...')
            continue
    pool.close()
    pool.join()


print('Vulnerabilities', find_vulnerabilities)
