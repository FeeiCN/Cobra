import multiprocessing
from cobra.engine.match import Match
from cobra.engine.rules import Rules
from cobra.utils.log import logger

r = Rules()
vulnerabilities = r.vulnerabilities
languages = r.languages
frameworks = r.frameworks
rules = r.rules


def scan_single(target_directory, rule):
    Match(target_directory).single(rule)


def store():
    pass


pool = multiprocessing.Pool()


def scan(target_directory):
    if len(rules) == 0:
        logger.critical('no rules!')
    for idx, rule in enumerate(rules):
        print(rule)
        if rule['language'] in languages:
            rule['extensions'] = languages[rule['language']]
            pool.apply_async(scan_single, args=(target_directory, rule), callback=store)
        else:
            print(rule)
            logger.critical('unset language!')
            continue
    pool.close()
    pool.join()
