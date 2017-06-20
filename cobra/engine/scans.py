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
    return Match(target_directory).get(rule)


def store(result):
    print(result)


def scan(target_directory):
    pool = multiprocessing.Pool()
    if len(rules) == 0:
        logger.critical('no rules!')
        return False
    for idx, rule in enumerate(rules):
        logger.info("""Push Rule
                     > index: {idx}
                     > name: {name}
                     > status: {status}
                     > language: {language}
                     > vid: {vid}""".format(
            idx=idx,
            name=rule['name']['en'],
            status=rule['status'],
            language=rule['language'],
            vid=rule['vid'],
            match=rule['match']
        ))
        if rule['status'] is False:
            logger.info('rule disabled, continue...')
            continue
        if rule['language'] in languages:
            rule['extensions'] = languages[rule['language']]
            pool.apply_async(scan_single, args=(target_directory, rule), callback=store)
        else:
            logger.critical('unset language, continue...')
            continue
    pool.close()
    pool.join()
