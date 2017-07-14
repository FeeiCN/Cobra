# -*- coding: utf-8 -*-

"""
    engine
    ~~~~~~

    Implements scan engine

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import re
import traceback
import subprocess
import multiprocessing
from .rule import Rule
from .utils import Tool
from .log import logger
from .result import VulnerabilityResult
from .ast import AST
from prettytable import PrettyTable


def scan_single(target_directory, single_rule):
    try:
        return SingleRule(target_directory, single_rule).process()
    except Exception as e:
        traceback.print_exc()


def scan(target_directory):
    r = Rule()
    vulnerabilities = r.vulnerabilities
    languages = r.languages
    frameworks = r.frameworks
    rules = r.rules
    find_vulnerabilities = []

    def store(result):
        if result is not None and isinstance(result, list) is True:
            for res in result:
                find_vulnerabilities.append(res)
        else:
            logger.debug('Not found vulnerabilities on this rule!')

    pool = multiprocessing.Pool()
    if len(rules) == 0:
        logger.critical('no rules!')
        return False
    logger.info('Push Rules ({rc})'.format(rc=len(rules)))
    for idx, single_rule in enumerate(rules):
        if single_rule['status'] is False:
            logger.debug('[RULE] OFF, CONTINUE...')
            continue
        # SR(Single Rule)
        logger.info(""" > Push {idx}.{name}({language})""".format(
            idx=idx,
            name=single_rule['name'],
            language=single_rule['language']
        ))
        if single_rule['language'] in languages:
            single_rule['extensions'] = languages[single_rule['language']]['extensions']
            pool.apply_async(scan_single, args=(target_directory, single_rule), callback=store)
        else:
            logger.critical('unset language, continue...')
            continue
    pool.close()
    pool.join()
    table = PrettyTable(["ID", "VUL", 'Rule', "Target", 'Commit Information'])
    for idx, x in enumerate(find_vulnerabilities):
        rule = x.rule_name
        trigger = '{fp}:{ln}'.format(fp=x.file_path, ln=x.line_number)
        commit = '@{author}({time})'.format(author=x.commit_author, time=x.commit_time)
        row = [idx, x.vulnerability, rule, trigger, commit]
        table.add_row(row)
    vn = len(find_vulnerabilities)
    if vn == 0:
        logger.info('Not found vulnerability!')
    else:
        logger.info("Vulnerabilities ({vn})\r\n{table}".format(vn=len(find_vulnerabilities), table=table))
    return True


class SingleRule(object):
    def __init__(self, target_directory, single_rule):
        self.directory = target_directory
        self.find = Tool().find
        self.grep = Tool().grep
        self.sr = single_rule
        # Single Rule Vulnerabilities
        """
        [
            vr
        ]
        """
        self.rule_vulnerabilities = []

    def origin_results(self):
        if self.sr['match'] == "":
            # find
            filters = []
            for index, e in enumerate(self.sr['extensions']):
                if index > 1:
                    filters.append('-o')
                filters.append('-name')
                filters.append('*' + e)
            # Find Special Ext Files
            param = [self.find, self.directory, "-type", "f"] + filters
        else:
            # grep
            filters = []
            for e in self.sr['extensions']:
                filters.append('--include=*' + e)

            # explode dirs
            explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [self.grep, "-s", "-n", "-r", "-P"] + filters + [self.sr['match'], self.directory]
        try:
            p = subprocess.Popen(param, stdout=subprocess.PIPE)
            result, error = p.communicate()
        except Exception as e:
            traceback.print_exc()
            logger.critical('match exception ({e})'.format(e=e.message))
            return None
        if error is not None:
            logger.critical(error)
        return result

    def process(self):
        """
        Process Single Rule
        :return: SRV(Single Rule Vulnerabilities)
        """
        origin_results = self.origin_results()
        # exists result
        if origin_results == '' or origin_results is None:
            logger.debug('[ORIGIN] NOT FOUND!')
            return None

        origin_vulnerabilities = str(origin_results).strip().split("\n")
        for index, origin_vulnerability in enumerate(origin_vulnerabilities):
            origin_vulnerability = origin_vulnerability.strip()
            logger.debug('[ORIGIN] {line}'.format(line=origin_vulnerability))
            if origin_vulnerability == '':
                logger.debug(' > continue...')
                continue
            vulnerability = self.parse_match(origin_vulnerability)
            is_test = False
            try:
                is_vulnerability, status_code = Core(self.directory, vulnerability, self.sr, 'project name', ['whitelist1', 'whitelist2'], test=is_test, index=index).scan()
                if is_vulnerability:
                    logger.debug('Found {code}'.format(code=status_code))
                    self.rule_vulnerabilities.append(vulnerability)
                else:
                    logger.debug('Not vulnerability: {code}'.format(code=status_code))
            except Exception as e:
                traceback.print_exc()
        logger.info('   > RID: {vn} Vulnerabilities: {count}'.format(vn=self.sr['name'], count=len(self.rule_vulnerabilities)))
        return self.rule_vulnerabilities

    def parse_match(self, single_match):
        mr = VulnerabilityResult()
        # grep result
        if ':' in single_match:
            #
            # Rules
            #
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:211:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:2134:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:21111:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # Projects/cobra/cobra/tests/examples/vulnerabilities.php:212344:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            try:
                mr.file_path, mr.line_number, mr.code_content = re.findall(r'(.*):(\d+):(.*)', single_match)[0]
            except Exception as e:
                logger.warning('match line parse exception')
                mr.file_path = ''
                mr.code_content = ''
                mr.line_number = 0
        else:
            # find result
            mr.file_path = single_match
            mr.code_content = ''
            mr.line_number = 0
        # vulnerability information
        mr.rule_name = self.sr['name']
        mr.vulnerability = self.sr['vulnerability']

        # committer
        from .pickup import Git
        c_ret, c_author, c_time = Git.committer(mr.file_path, mr.line_number)
        if c_ret:
            mr.commit_author = c_author
            mr.commit_time = c_time
        return mr


class Core(object):
    def __init__(self, target_directory, vulnerability_result, single_rule, project_name, white_list, test=False, index=None):
        """
        Initialize
        :param: target_directory:
        :param: vulnerability_result:
        :param single_rule: rule info
        :param project_name: project name
        :param white_list: white-list
        :param test: is test
        :param index: vulnerability index
        """
        self.data = []

        self.target_directory = target_directory

        self.file_path = vulnerability_result.file_path.strip()
        self.line_number = vulnerability_result.line_number
        self.code_content = vulnerability_result.code_content.strip()

        self.rule_match = single_rule['match'].strip()
        self.rule_match2 = single_rule['match2']
        self.rule_match2_block = single_rule['match2-block']
        self.rule_repair = single_rule['repair']
        self.repair_block = single_rule['repair-block']

        self.project_name = project_name
        self.white_list = white_list
        self.test = test

        self.status = None
        self.status_init = 0
        self.status_fixed = 2

        # const.py
        self.repair_code = None
        self.repair_code_init = 0
        self.repair_code_fixed = 1
        self.repair_code_not_exist_file = 4000
        self.repair_code_special_file = 4001
        self.repair_code_whitelist = 4002
        self.repair_code_test_file = 4003
        self.repair_code_annotation = 4004
        self.repair_code_modify = 4005
        self.repair_code_empty_code = 4006
        self.repair_code_const_file = 4007
        self.repair_code_third_party = 4008

        self.method = None
        logger.debug("""[VERIFY-VULNERABILITY] ({index})
        > File: `{file}:{line}`
        > Code: `{code}`
        > Match2: `{m2}({m2b})`
        > Repair: `{r}({rb})`""".format(
            index=index,
            file=self.file_path.replace(self.target_directory, ''),
            line=self.line_number,
            code=self.code_content,
            m2=self.rule_match2,
            m2b=self.rule_match2_block,
            r=self.rule_repair,
            rb=self.repair_block))

    def is_white_list(self):
        """
        Is white-list file
        :return: boolean
        """
        return self.file_path.split(self.target_directory, 1)[1] in self.white_list

    def is_special_file(self):
        """
        Is special file
        :method: According to the file name to determine whether the special file
        :return: boolean
        """
        special_paths = [
            '/node_modules/',
            '/bower_components/',
            '.min.js',
        ]
        for path in special_paths:
            if path in self.file_path:
                return True
        return False

    def is_test_file(self):
        """
        Is test case file
        :method: file name
        :return: boolean
        """
        test_paths = [
            '/test/',
            '/tests/',
            '/unitTests/'
        ]
        for path in test_paths:
            if path in self.file_path:
                return True
        return False

    def is_match_only_rule(self):
        """
        Whether only match the rules, do not parameter controllable processing
        :method: It is determined by judging whether the left and right sides of the regex_location are brackets
        :return: boolean
        """
        return self.rule_match[:1] == '(' and self.rule_match[-1] == ')'

    def is_annotation(self):
        """
        Is annotation
        :method: Judgment by matching comment symbols (skipped when self.is_match_only_rule condition is met)
               - PHP:  `#` `//` `\*` `*`
                    //asdfasdf
                    \*asdfasdf
                    #asdfasdf
                    *asdfasdf
               - Java:
        :return: boolean
        """
        match_result = re.findall(r"(#|\\\*|\/\/|\*)+", self.code_content)
        # Skip detection only on match
        if self.is_match_only_rule():
            return False
        else:
            return len(match_result) > 0

    def is_can_parse(self):
        """
        Whether to parse the parameter is controllable operation
        :return:
        """
        for language in AST.languages:
            if self.file_path[-len(language):].lower() == language:
                return True
        return False

    def scan(self):
        """
        Scan vulnerabilities
        :flow:
        - whitelist file
        - special file
        - test file
        - annotation
        - rule
        :return: is_vulnerability, code
        """
        self.method = 0
        if self.is_white_list():
            logger.debug("[RET] Whitelist")
            return False, 5001

        if self.is_special_file():
            logger.debug("[RET] Special File")
            return False, 5002

        if self.is_test_file():
            logger.debug("[RET] Test File")
            return True, 5003

        if self.is_annotation():
            logger.debug("[RET] Annotation")
            return False, 5004

        if self.is_match_only_rule():
            logger.debug("[ONLY-MATCH] {0}".format(self.rule_match))
            found_vul = True
        else:
            logger.debug('[NOT-ONLY-MATCH]')
            found_vul = False
            # parameter is controllable
            if self.is_can_parse() and (self.rule_repair is not None or self.rule_match2 is not None):
                try:
                    ast = AST(self.rule_match, self.file_path, self.line_number, self.code_content)
                    # Match2
                    if self.rule_match2 is not None:
                        is_match, data = ast.match(self.rule_match2, self.rule_match2_block)
                        if is_match:
                            logger.debug('[MATCH2] True')
                            return True, 1001
                        else:
                            logger.debug('[MATCH2] False')
                            return False, 1002
                    param_is_controllable, data = ast.is_controllable_param()
                    if param_is_controllable:
                        logger.debug('[RET] Param is controllable')
                        is_repair, data = ast.match(self.rule_repair, self.repair_block)
                        if is_repair:
                            # fixed
                            logger.debug('[RET] Vulnerability Fixed')
                            return False, 1002
                        else:
                            logger.debug('Repair: Not fixed')
                            found_vul = True
                    else:
                        logger.debug('[RET] Param Not Controllable')
                        return False, 4002
                except Exception as e:
                    traceback.print_exc()
                    return False, 4004

        if found_vul:
            self.code_content = self.code_content.encode('unicode_escape')
            if len(self.code_content) > 512:
                self.code_content = self.code_content[:500]
            self.status = self.status_init
            self.repair_code = self.repair_code_init
            return True, 1001
        else:
            logger.debug("[RET] Not found vulnerability")
            return False, 4002
