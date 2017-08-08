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
import os
import re
import json
import traceback
import subprocess
import multiprocessing
from .rule import Rule
from .utils import Tool
from .log import logger
from .config import running_path
from .result import VulnerabilityResult
from .ast import AST
from prettytable import PrettyTable


class Running:
    def __init__(self, sid):
        self.sid = sid
        self.running_path = os.path.join(running_path, sid)

    def init(self):
        data = {
            'status': 'running',
            'report': ''
        }
        data = json.dumps(data)
        with open(self.running_path, 'w') as f:
            f.writelines(data)

    def completed(self, report):
        data = {
            'status': 'done',
            'report': report
        }
        data = json.dumps(data)
        with open(self.running_path, 'w+') as f:
            f.writelines(data)

    def get(self):
        with open(self.running_path) as f:
            result = f.readline()
        return json.loads(result)

    def is_file(self):
        return os.path.isfile(self.running_path)


def score2level(score):
    level_score = {
        'CRITICAL': [9, 10],
        'HIGH': [6, 7, 8],
        'MEDIUM': [3, 4, 5],
        'LOW': [1, 2]
    }
    score = int(score)
    level = None
    for l in level_score:
        if score in level_score[l]:
            level = l
    if level is None:
        return 'Unknown'
    else:
        return '{l}-{s}: {ast}'.format(l=level[:1], s=score, ast='☆' * score)


def scan_single(target_directory, single_rule):
    try:
        return SingleRule(target_directory, single_rule).process()
    except Exception as e:
        traceback.print_exc()


def scan(target_directory, sid=None, special_rules=None):
    r = Rule()
    vulnerabilities = r.vulnerabilities
    languages = r.languages
    frameworks = r.frameworks
    rules = r.rules(special_rules)
    find_vulnerabilities = []

    def store(result):
        if result is not None and isinstance(result, list) is True:
            for res in result:
                res.file_path = res.file_path.replace(target_directory, '')
                find_vulnerabilities.append(res)
        else:
            logger.debug('Not found vulnerabilities on this rule!')

    pool = multiprocessing.Pool()
    if len(rules) == 0:
        logger.critical('no rules!')
        return False
    logger.info('[PUSH] {rc} Rules'.format(rc=len(rules)))
    for idx, single_rule in enumerate(rules):
        if single_rule['status'] is False:
            logger.info('[CVI-{cvi}] [STATUS] OFF, CONTINUE...'.format(cvi=single_rule['id']))
            continue
        # SR(Single Rule)
        logger.debug("""[PUSH] [CVI-{cvi}] {idx}.{name}({language})""".format(
            cvi=single_rule['id'],
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

    # print
    table = PrettyTable(['#', 'CVI', 'VUL', 'Rule(ID/Name)', 'Lang', 'Level-Score', 'Target-File:Line-Number', 'Commit(Author/Time)', 'Source Code Content'])
    table.align = 'l'
    trigger_rules = []
    for idx, x in enumerate(find_vulnerabilities):
        trigger = '{fp}:{ln}'.format(fp=x.file_path, ln=x.line_number)
        commit = '@{author},{time}'.format(author=x.commit_author, time=x.commit_time)
        level = score2level(x.level)
        cvi = x.id[0:3]
        if cvi in vulnerabilities:
            cvn = vulnerabilities[cvi]
        else:
            cvn = 'Unknown'
        row = [idx + 1, x.id, cvn, x.rule_name, x.language, level, trigger, commit, x.code_content.decode('utf-8')[:100].strip()]
        table.add_row(row)
        if x.id not in trigger_rules:
            logger.debug(' > trigger rule (CVI-{cvi})'.format(cvi=x.id))
            trigger_rules.append(x.id)
    vn = len(find_vulnerabilities)
    if vn == 0:
        logger.info('Not found vulnerability!')
    else:
        logger.info(" > Trigger Rules: {tr} Vulnerabilities ({vn})\r\n{table}".format(tr=len(trigger_rules), vn=len(find_vulnerabilities), table=table))

    # completed running data
    if sid is not None:
        report = 'http://xxx.test.com'
        running = Running(sid)
        running.completed(report)
    return True


class SingleRule(object):
    def __init__(self, target_directory, single_rule):
        self.target_directory = target_directory
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
            param = [self.find, self.target_directory, "-type", "f"] + filters
        else:
            # grep
            filters = []
            for e in self.sr['extensions']:
                filters.append('--include=*' + e)

            # explode dirs
            explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s Suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [self.grep, "-s", "-n", "-r", "-P"] + filters + [self.sr['match'], self.target_directory]
        try:
            p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            result, error = p.communicate()
        except Exception as e:
            traceback.print_exc()
            logger.critical('match exception ({e})'.format(e=e.message))
            return None
        if len(error) is not 0:
            logger.critical('[CVI-{cvi}] [ORIGIN] [ERROR] {err}'.format(cvi=self.sr['id'], err=error.strip()))
        return result

    def process(self):
        """
        Process Single Rule
        :return: SRV(Single Rule Vulnerabilities)
        """
        origin_results = self.origin_results()
        # exists result
        if origin_results == '' or origin_results is None:
            logger.debug('[CVI-{cvi}] [ORIGIN] NOT FOUND!'.format(cvi=self.sr['id']))
            return None

        origin_vulnerabilities = str(origin_results).strip().split("\n")
        for index, origin_vulnerability in enumerate(origin_vulnerabilities):
            origin_vulnerability = origin_vulnerability.strip()
            logger.debug('[CVI-{cvi}] [ORIGIN] {line}'.format(cvi=self.sr['id'], line=origin_vulnerability))
            if origin_vulnerability == '':
                logger.debug(' > continue...')
                continue
            vulnerability = self.parse_match(origin_vulnerability)
            if vulnerability is None:
                logger.debug('Not vulnerability, continue...')
                continue
            is_test = False
            try:
                is_vulnerability, status_code = Core(self.target_directory, vulnerability, self.sr, 'project name', ['whitelist1', 'whitelist2'], test=is_test, index=index).scan()
                if is_vulnerability:
                    logger.debug('[CVI-{cvi}] [RET] Found {code}'.format(cvi=self.sr['id'], code=status_code))
                    self.rule_vulnerabilities.append(vulnerability)
                else:
                    logger.debug('Not vulnerability: {code}'.format(code=status_code))
            except Exception as e:
                traceback.print_exc()
        logger.debug('[CVI-{cvi}] {vn} Vulnerabilities: {count}'.format(cvi=self.sr['id'], vn=self.sr['name'], count=len(self.rule_vulnerabilities)))
        return self.rule_vulnerabilities

    def parse_match(self, single_match):
        mr = VulnerabilityResult()
        # grep result
        if ':' in single_match:
            #
            # Rules
            #
            # v.php:2:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # v.php:211:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # v.php:2134:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # v.php:21111:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            # v.php:212344:$password = "C787AFE9D9E86A6A6C78ACE99CA778EE";
            try:
                mr.line_number, mr.code_content = re.findall(r':(\d+):(.*)', single_match)[0]
                mr.file_path = single_match.split(':{n}:'.format(n=mr.line_number))[0]
            except Exception as e:
                logger.warning('match line parse exception')
                mr.file_path = ''
                mr.code_content = ''
                mr.line_number = 0
        else:
            if 'Binary file' in single_match:
                return None
            else:
                # find result
                mr.file_path = single_match
                mr.code_content = ''
                mr.line_number = 0
        # vulnerability information
        mr.rule_name = self.sr['name']
        mr.id = self.sr['id']
        mr.language = self.sr['language']
        mr.solution = self.sr['solution']
        mr.level = self.sr['level']

        # committer
        from .pickup import Git
        c_ret, c_author, c_time = Git.committer(self.target_directory, mr.file_path, mr.line_number)
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
        self.rule_match_mode = single_rule['match-mode']
        self.rule_match2 = single_rule['match2']
        self.rule_match2_block = single_rule['match2-block']
        self.rule_repair = single_rule['repair']
        self.repair_block = single_rule['repair-block']
        self.cvi = single_rule['id']

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
        logger.debug("""[CVI-{cvi}] [VERIFY-VULNERABILITY] ({index})
        > File: `{file}:{line}`
        > Code: `{code}`
        > Match2: `{m2}({m2b})`
        > Repair: `{r}({rb})`""".format(
            cvi=single_rule['id'],
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
        if self.rule_match_mode == 'regex-only-match':
            return True
        else:
            return False

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
        match_result = re.findall(r"(#|\\\*|\/\/)+", self.code_content)
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

        if self.is_annotation():
            logger.debug("[RET] Annotation")
            return False, 5004

        if self.is_match_only_rule():
            logger.debug("[CVI-{cvi}] [ONLY-MATCH]".format(cvi=self.cvi))
            found_vul = True
            if self.rule_repair is not None:
                logger.debug('[VERIFY-REPAIR]')
                ast = AST(self.rule_match, self.target_directory, self.file_path, self.line_number, self.code_content)
                is_repair, data = ast.match(self.rule_repair, self.repair_block)
                if is_repair:
                    # fixed
                    logger.debug('[CVI-{cvi}] [RET] Vulnerability Fixed'.format(cvi=self.cvi))
                    return False, 1002
                else:
                    logger.debug('[CVI-{cvi}] [REPAIR] [RET] Not fixed'.format(cvi=self.cvi))
                    found_vul = True
        else:
            logger.debug('[CVI-{cvi}] [NOT-ONLY-MATCH]'.format(cvi=self.cvi))
            found_vul = False
            # parameter is controllable
            if self.is_can_parse() and (self.rule_repair is not None or self.rule_match2 is not None):
                try:
                    ast = AST(self.rule_match, self.target_directory, self.file_path, self.line_number, self.code_content)
                    # Match2
                    if self.rule_match2 is not None:
                        is_match, data = ast.match(self.rule_match2, self.rule_match2_block)
                        if is_match:
                            logger.debug('[CVI-{cvi}] [MATCH2] True'.format(cvi=self.cvi))
                            return True, 1001
                        else:
                            logger.debug('[CVI-{cvi}] [MATCH2] False'.format(cvi=self.cvi))
                            return False, 1002
                    param_is_controllable, data = ast.is_controllable_param()
                    if param_is_controllable:
                        logger.debug('[CVI-{cvi}] [RET] Param is controllable'.format(cvi=self.cvi))
                        is_repair, data = ast.match(self.rule_repair, self.repair_block)
                        if is_repair:
                            # fixed
                            logger.debug('[CVI-{cvi}] [RET] Vulnerability Fixed'.format(cvi=self.cvi))
                            return False, 1002
                        else:
                            logger.debug('[CVI-{cvi}] [REPAIR] [RET] Not fixed'.format(cvi=self.cvi))
                            found_vul = True
                    else:
                        logger.debug('[CVI-{cvi}] [RET] Param Not Controllable'.format(cvi=self.cvi))
                        return False, 4002
                except Exception as e:
                    traceback.print_exc()
                    return False, 4004

        if found_vul:
            self.code_content = self.code_content
            if len(self.code_content) > 512:
                self.code_content = self.code_content[:500]
            self.status = self.status_init
            self.repair_code = self.repair_code_init
            return True, 1001
        else:
            logger.debug("[RET] Not found vulnerability")
            return False, 4002
