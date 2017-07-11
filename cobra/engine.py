# -*- coding: utf-8 -*-

"""
    engine
    ~~~~~~

    Implements engine

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import re
import traceback
import subprocess
import multiprocessing
from .config import Config, Rules
from pip.req import parse_requirements
from .utils import Tool
from .log import logger
from .result import VulnerabilityResult
from .pickup import File


def scan_single(target_directory, single_rule):
    return SingleRule(target_directory, single_rule).process()


def scan(target_directory):
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

    def store(result):
        if result is not None and isinstance(result, list) is True:
            for r in result:
                find_vulnerabilities.append(r)
        else:
            logger.debug('Not found vulnerabilities on this rule!')

    pool = multiprocessing.Pool()
    if len(rules) == 0:
        logger.critical('no rules!')
        return False
    for idx, single_rule in enumerate(rules):
        # SR(Single Rule)
        logger.debug("""Push Rule
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
    logger.info('> Rules: {rc}'.format(rc=len(rules)))
    pool.close()
    pool.join()

    for x in find_vulnerabilities:
        print(x)


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
            mode = 'Find'
            filters = []
            for index, e in enumerate(self.sr['extensions']):
                if index > 1:
                    filters.append('-o')
                filters.append('-name')
                filters.append('*' + e)
            # Find Special Ext Files
            param = [self.find, self.directory, "-type", "f"] + filters
        else:
            mode = 'Grep'
            filters = []
            for e in self.sr['extensions']:
                filters.append('--include=*' + e)

            # explode dirs
            explode_dirs = ['.svn', '.cvs', '.hg', '.git', '.bzr']
            for explode_dir in explode_dirs:
                filters.append('--exclude-dir={0}'.format(explode_dir))

            # -s suppress error messages / -n Show Line number / -r Recursive / -P Perl regular expression
            param = [self.grep, "-s", "-n", "-r", "-P"] + filters + [self.sr['match'], self.directory]
        logger.debug(' '.join(param))
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
            logger.debug('Not found any match...')
            return None

        origin_vulnerabilities = str(origin_results).strip().split("\n")
        for index, origin_vulnerability in enumerate(origin_vulnerabilities):
            origin_vulnerability = origin_vulnerability.strip()
            logger.debug(' > origin: {line}'.format(line=origin_vulnerability))
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
        logger.info('  > RID: {rid}({vn}) Vulnerabilities: {count}'.format(rid=self.sr['vid'], vn=self.sr['name']['en'], count=len(self.rule_vulnerabilities)))
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
        return mr


class Detection(object):
    def __init__(self, target_directory, files):
        self.target_directory = target_directory
        self.directory = os.path.abspath(self.target_directory)
        self.files = files
        self.lang = None
        self.requirements = None

    @property
    def language(self):
        tmp_language = None
        for ext, ext_info in self.files:
            logger.debug("{ext} {count}".format(ext=ext, count=ext_info['count']))
            rules = Config().rule()
            for language, language_info in rules['languages'].items():
                if ext in language_info['extensions']:
                    if 'chiefly' in language_info and language_info['chiefly'].lower() == 'true':
                        logger.debug('found the chiefly language({language}), maybe have largest, continue...'.format(language=language))
                        self.lang = language
                    else:
                        logger.debug('not chiefly, continue...'.format(language=language))
                        tmp_language = language
            if self.lang is None:
                logger.debug('not found chiefly language, use the largest language(language) replace'.format(language=tmp_language))
                self.lang = tmp_language
        logger.debug('main language({main_language}), tmp language({tmp_language})'.format(tmp_language=tmp_language, main_language=self.lang))
        return self.lang

    @property
    def framework(self):
        # initialize requirements data
        self._requirements()
        # TODO
        return 'Unknown Framework'
        frameworks = Config().rule()['languages'][self.lang]['frameworks']
        for framework in frameworks:
            # single framework
            logger.debug('{frame} - {code}'.format(frame=framework['name'], code=framework['code']))
            for method, rule in framework['rules'].items():
                rule = rule.strip().lower()
                # single rule
                if method == 'requirements':
                    logger.debug(' - requirements: {module}'.format(module=rule))
                    if rule in self.requirements:
                        return framework['name']
                elif method == 'file':
                    pass
                elif method == 'folder':
                    pass
        return 'Unknown Framework'

    def _requirements(self):
        requirements_txt = os.path.join(self.directory, 'requirements.txt')
        logger.debug(requirements_txt)
        if os.path.isfile(requirements_txt):
            requirements = parse_requirements(requirements_txt, session=False)
            self.requirements = [req.name.strip().lower() for req in requirements]
            logger.debug('requirements modules count: {count} ({modules})'.format(count=len(self.requirements), modules=','.join(self.requirements)))
        else:
            logger.debug('requirements.txt not found!')
            self.requirements = []


class Parse(object):
    def __init__(self, rule, file_path, line, code, ):
        self.data = []
        self.rule = rule
        self.file_path = file_path
        self.line = line
        self.code = code
        self.param_name = None
        self.param_value = None
        self.language = None
        languages = ['php', 'java']
        for language in languages:
            if self.file_path[-len(language):].lower() == language:
                self.language = language

        # Parse rule
        self.regex = {
            'java': {
                'functions': r'(?:public|protected|private|static|\s) +[\w\<\>\[\]]+\s+(\w+) *\([^\)]*\) *(?:\{?|[^;])',
                'string': r"(?:[\"])(.*)(?:[\"])",
                'assign_string': r"String\s{0}\s=\s\"(.*)\";",
                'annotation': r"(\\\*|\/\/|\*)+"
            },
            'php': {
                'functions': r'(?:function\s+)(\w+)\s*\(',
                'string': r"(?:['\"])(.*)(?:[\"'])",
                'assign_string': r"({0}\s?=\s?[\"'](.*)(?:['\"]))",
                'annotation': r"(#|\\\*|\/\/|\*)+",
                'variable': r'(\$[a-zA-Z_\x7f-\xff][a-zA-Z0-9_\x7f-\xff]*)',
                # Need match
                #    $url = $_GET['test'];
                #    $url = $_POST['test'];
                #    $url = $_REQUEST['test'];
                #    $url = $_SERVER['user_agent'];
                #    $v = trim($_GET['t']);
                # Don't match
                #    $url = $_SERVER
                #    $url = $testsdf;
                'assign_out_input': r'({0}\s?=\s?.*\$_[GET|POST|REQUEST|SERVER|COOKIE]+(?:\[))'
            }
        }
        logger.debug("Language: `{language}`".format(language=self.language))

    def functions(self):
        """
        get all functions in this file
        :return:
        """
        grep = Tool().grep
        if self.language not in self.regex:
            logger.info("Undefined language's functions regex {0}".format(self.language))
            return False
        regex_functions = self.regex[self.language]['functions']
        param = [grep, "-s", "-n", "-r", "-P"] + [regex_functions, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE)
        result = p.communicate()
        if len(result[0]):
            functions = {}
            lines = str(result[0]).strip().split("\n")
            prev_function_name = ''
            for index, line in enumerate(lines):
                line = line.strip()
                if line == '':
                    logger.info('Empty')
                    continue
                function = line.split(':')
                if len(function) < 2:
                    logger.info("Not found(:)")

                regex_annotation = self.regex[self.language]['annotation']
                string = re.findall(regex_annotation, function[1].strip())
                if len(string) >= 1 and string[0] != '':
                    logger.info(logger.info("This function is annotation"))

                function_name = re.findall(regex_functions, function[1].strip())
                if len(function_name) == 1:
                    function_name = function_name[0]
                    if index > 0 and prev_function_name in functions:
                        functions[prev_function_name]['end'] = function[0]
                    prev_function_name = function_name
                    functions[function_name] = {
                        'start': function[0],
                        'end': None  # next function's start
                    }
                else:
                    logger.info("Can't get function name: {0}".format(line))
            end = sum(1 for l in open(self.file_path))
            for name, value in functions.items():
                if value['end'] is None:
                    functions[name]['end'] = end
            return functions
        else:
            return False

    def block_code(self, block_position):
        """
        Get code block
        :param block_position:
                0:up
                1:down
                2:location_line
        :return:
        """
        if block_position == 2:
            if self.line is None or self.line == 0:
                logger.critical("Line exception: {0}".format(self.line))
                return False
            line_rule = '{0}p'.format(self.line)
            code = File(self.file_path).lines(line_rule)
            code = code.strip()
            return code
        else:
            block_start = 1
            block_end = 0
            functions = self.functions()
            if functions:
                for function_name, function_value in functions.items():
                    if int(function_value['start']) < int(self.line) < int(function_value['end']):
                        in_this_function = '<---- {0}'.format(self.line)
                        if block_position == 0:
                            block_start = function_value['start']
                            block_end = int(self.line) - 1
                        elif block_position == 1:
                            block_start = int(self.line)
                            block_end = int(function_value['end']) - 1
                        logger.debug("Trigger line's function name: {0} ({1} - {2}) {3}".format(function_name, function_value['start'], function_value['end'], in_this_function))
            else:
                if block_position == 0:
                    block_start = 1
                    block_end = int(self.line) - 1
                elif block_position == 1:
                    block_start = int(self.line) + 1
                    block_end = sum(1 for l in open(self.file_path))
                logger.debug("Not function anything `function`, will split file")
            # get param block code
            line_rule = "{0},{1}p".format(block_start, block_end)
            code = File(self.file_path).lines(line_rule)
            logger.info('Get code: {0} - {1}p'.format(block_start, block_end))
            return code

    def is_controllable_param(self):
        """
        is controllable param
        :return:
        """
        logger.debug('Is controllable param')
        param_name = re.findall(self.rule, self.code)
        if len(param_name) == 1:
            param_name = param_name[0].strip()
            self.param_name = param_name
            logger.debug('Param: `{0}`'.format(param_name))
            # all is string
            regex_string = self.regex[self.language]['string']
            string = re.findall(regex_string, param_name)
            if len(string) >= 1 and string[0] != '':
                regex_get_variable_result = re.findall(self.regex[self.language]['variable'], param_name)
                len_regex_get_variable_result = len(regex_get_variable_result)
                if len_regex_get_variable_result >= 1:
                    # TODO
                    # 'ping $v1 $v2'
                    # foreach $vn
                    param_name = regex_get_variable_result[0]
                    logger.info("String's variables: `{variables}`".format(variables=','.join(regex_get_variable_result)))
                else:
                    logger.debug("String have variables: `No`")
                    return False, self.data
            logger.debug("String have variables: `Yes`")

            # variable
            if param_name[:1] == '$':
                logger.debug("Is variable: `Yes`")

                # Get assign code block
                param_block_code = self.block_code(0)
                if param_block_code is False:
                    logger.debug("Can't get assign code block")
                    return True, self.data
                logger.debug('Code assign code block: ```{language}\r\n{block}```'.format(language=self.language, block=param_block_code))

                # Is assign out input
                regex_get_param = self.regex[self.language]['assign_out_input'].format(re.escape(param_name))
                regex_get_param_result = re.findall(regex_get_param, param_block_code)
                if len(regex_get_param_result) >= 1:
                    self.param_value = regex_get_param_result[0]
                    logger.debug("Is assign out input: `Yes`")
                    return True, self.data
                logger.debug("Is assign out input: `No`")

                # Is function's param
                regex_function_param = r'(function\s*\w+\s*\(.*{0})'.format(re.escape(param_name))
                regex_function_param_result = re.findall(regex_function_param, param_block_code)
                if len(regex_function_param_result) >= 1:
                    self.param_value = regex_function_param_result[0]
                    logger.debug("Is function's param: `Yes`")
                    return True, self.data
                logger.debug("Is function's param: `No`")

                # Is assign CONST
                uc_rule = r'{0}\s?=\s?([A-Z_]*)'.format(re.escape(param_name))
                uc_rule_result = re.findall(uc_rule, param_block_code)
                if len(uc_rule_result) >= 1:
                    logger.debug("Is assign CONST: Yes `{0} = {1}`".format(param_name, uc_rule_result[0]))
                    return False, self.data
                logger.debug("Is assign CONST: `No`")

                # Is assign string
                regex_assign_string = self.regex[self.language]['assign_string'].format(re.escape(param_name))
                string = re.findall(regex_assign_string, param_block_code)
                if len(string) >= 1 and string[0] != '':
                    logger.debug("Is assign string: `Yes`")
                    return False, self.data
                logger.debug("Is assign string: `No`")
                return True, self.data
            else:
                if self.language == 'java':
                    # Java variable didn't have `$`
                    param_block_code = self.block_code(0)
                    if param_block_code is False:
                        logger.debug("Can't get block code")
                        return True, self.data
                    logger.debug("Block code: ```{language}\r\n{code}```".format(language=self.language, code=param_block_code))
                    regex_assign_string = self.regex[self.language]['assign_string'].format(re.escape(param_name))
                    string = re.findall(regex_assign_string, param_block_code)
                    if len(string) >= 1 and string[0] != '':
                        logger.debug("Is assign string: `Yes`")
                        return False, self.data
                    logger.debug("Is assign string: `No`")

                    # Is assign out data
                    regex_get_param = r'String\s{0}\s=\s\w+\.getParameter(.*)'.format(re.escape(param_name))
                    get_param = re.findall(regex_get_param, param_block_code)
                    if len(get_param) >= 1 and get_param[0] != '':
                        logger.debug("Is assign out data: `Yes`")
                        return False, self.data
                    logger.debug("Is assign out data: `No`")
                    return True, self.data
                logger.info("Not Java/PHP, can't parse")
                return False, self.data
        else:
            logger.warning("Can't get `param`, check built-in rule")
            return False, self.data

    def is_repair(self, repair_rule, block_repair):
        """
        Is repair
        :param repair_rule:
        :param block_repair:
        :return:
        """
        self.data = []
        logger.info('**Is Repair**')
        block_repair_desc = {
            0: 'UP',
            1: 'DOWN',
            2: 'CURRENT'
        }
        logger.debug('Block code: {block}'.format(block=block_repair_desc[block_repair]))
        code = self.block_code(block_repair)
        if code is False:
            logger.debug("Can't get repair block code")
            return False, self.data
        # replace repair {{PARAM}} const
        if '{{PARAM}}' in repair_rule:
            repair_rule = repair_rule.replace('{{PARAM}}', self.param_name)
        logger.debug("Block code: {code}".format(code=code))
        repair_result = re.findall(repair_rule, code)
        logger.debug("Repair code: {0}".format(repair_result))
        if len(repair_result) >= 1:
            return True, self.data
        else:
            return False, self.data


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

        self.rule_location = single_rule['match'].strip()
        self.rule_repair = single_rule['repair'].strip()
        self.block_repair = single_rule['block']

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
        logger.debug("""Vulnerability({index})
        > File: `{file}:{line}`
        > Code: `{code}`
        > Repair Code: `{repair}`""".format(
            index=index,
            file=self.file_path.replace(self.target_directory, ''),
            line=self.line_number,
            code=self.code_content,
            repair=self.repair_code))

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
        return self.rule_location[:1] == '(' and self.rule_location[-1] == ')'

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
        return self.file_path[-3:] == 'php' or self.file_path[-4:] == 'java'

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
            logger.info("[RET] Whitelist")
            return False, 5001

        if self.is_special_file():
            logger.info("[RET] Special File")
            return False, 5002

        if self.is_test_file():
            logger.info("[RET] Test File")
            return True, 5003

        if self.is_annotation():
            logger.info("[RET] Annotation")
            return False, 5004

        if self.is_match_only_rule():
            logger.debug("Only Rule: {0}".format(self.rule_location))
            found_vul = True
        else:
            found_vul = False
            # parameter is controllable
            if self.is_can_parse() and self.rule_repair.strip() != '':
                try:
                    parse_instance = Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                    param_is_controllable, data = parse_instance.is_controllable_param()
                    if param_is_controllable:
                        logger.info('[RET] Param is controllable')
                        is_repair, data = parse_instance.is_repair(self.rule_repair, self.block_repair)
                        if is_repair:
                            # fixed
                            logger.info('[RET] Vulnerability Fixed')
                            return False, 1002
                        else:
                            logger.info('Repair: Not fixed')
                            found_vul = True
                    else:
                        logger.debug('[RET] Param Not Controllable')
                        return False, 4002
                except:
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

    def repair(self):
        """
        Scan vulnerabilities is repair
        :flow:
        - exist file [add]
        - test file
        - whitelist file
        - special file
        - annotation
        - rule
        :return: (Status, Result)
        """
        self.method = 1

        # Full path
        self.file_path = self.target_directory + self.file_path

        """
        When the targeting rule is empty or the line number is 0, it means that this type of language (all suffixes in that language) is counted as a vulnerability
        Their repair method is only one: delete the file
        """
        if self.rule_location == '' or self.line_number == 0:
            logger.info("Find special files: RID{0}".format(self.rule_id))
            # Check if the file exists
            if os.path.isfile(self.file_path) is False:
                # If the file is not found, the vulnerability state is fixed
                logger.info("Deleted file repair is complete {0}".format(self.file_path))
                self.status = self.status_fixed
                self.repair_code = self.repair_code_not_exist_file
                self.process_vulnerabilities()
                return
            else:
                return

        # Not exist file
        if os.path.isfile(self.file_path) is False:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_not_exist_file
            self.process_vulnerabilities()
            return

        # Test file
        if self.is_test_file():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_test_file
            self.process_vulnerabilities()
            return

        """
        Cobra Skip

        @cobra const
        `@[cC][oO][bB][rR][aA]\s*[cC][oO][nN][sS][tT]`
        """
        file_content = File(self.file_path).read_file()
        ret_regex_const = re.findall(r'@[cC][oO][bB][rR][aA]\s*[cC][oO][nN][sS][tT]', file_content)
        if len(ret_regex_const) > 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_const_file
            self.process_vulnerabilities()
            return

        """
        @cobra third-party
        `@[cC][oO][bB][rR][aA]\s*[tT][hH][iI][rR][dD]-[pP][aA][rR][tT][yY]`
        """
        ret_regex_third_party = re.findall(r'@[cC][oO][bB][rR][aA]\s*[tT][hH][iI][rR][dD]-[pP][aA][rR][tT][yY]', file_content)
        if len(ret_regex_third_party) > 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_third_party
            self.process_vulnerabilities()
            return

        # Remove the trigger code (actual file)
        trigger_code = File(self.file_path).lines("{0}p".format(self.line_number))
        if trigger_code is False:
            logger.critical("Failed to fetch the trigger code {0}".format(self.code_content))
            self.status = self.status_fixed
            self.repair_code = self.repair_code_empty_code
            self.process_vulnerabilities()
            return

        self.code_content = trigger_code

        # Whitelist
        if self.is_white_list():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_whitelist
            self.process_vulnerabilities()
            logger.info("In white list {0}".format(self.file_path))
            return

        # Special file
        if self.is_special_file():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_special_file
            self.process_vulnerabilities()
            logger.info("Special File: {0}".format(self.file_path))
            return

        # Annotation
        if self.is_annotation():
            self.status = self.status_fixed
            self.repair_code = self.repair_code_annotation
            self.process_vulnerabilities()
            logger.info("In Annotation {0}".format(self.code_content))
            return

        # Modify
        ret_regex = re.findall(self.rule_location, trigger_code.strip())
        if len(ret_regex) == 0:
            self.status = self.status_fixed
            self.repair_code = self.repair_code_modify
            self.process_vulnerabilities()
            return

        # Fixed
        if self.is_can_parse() and self.rule_repair.strip() != '':
            try:
                parse_instance = Parse(self.rule_location, self.file_path, self.line_number, self.code_content)
                if parse_instance.is_repair(self.rule_repair, self.block_repair):
                    logger.info("Static: repaired")
                    # Fixed
                    self.status = self.status_fixed
                    self.repair_code = self.repair_code_fixed
                    self.process_vulnerabilities()
                    return
                else:
                    logger.critical("[repair] not fixed")
                    return
            except:
                logger.info(traceback.print_exc())
                return
