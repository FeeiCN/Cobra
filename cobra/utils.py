# -*- coding: utf-8 -*-

"""
    utils
    ~~~~~

    Implements utils

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import shutil
import hashlib
import json
import base64
import os
import random
import re
import string
import sys
import time
import urllib
import requests
import json
import pipes

from .log import logger
from .config import Config, issue_history_path, core_path
from .__version__ import __version__, __python_version__, __platform__, __url__
from .exceptions import PickupException, NotExistException, AuthFailedException
from .pickup import Git, NotExistError, AuthError, Decompress
from .const import access_token

TARGET_MODE_GIT = 'git'
TARGET_MODE_FILE = 'file'
TARGET_MODE_FOLDER = 'folder'
TARGET_MODE_COMPRESS = 'compress'

OUTPUT_MODE_MAIL = 'mail'
OUTPUT_MODE_API = 'api'
OUTPUT_MODE_FILE = 'file'
OUTPUT_MODE_STREAM = 'stream'
PY2 = sys.version_info[0] == 2


class ParseArgs(object):
    def __init__(self, target, formatter, output, special_rules=None, a_sid=None):
        self.target = target
        self.formatter = formatter
        self.output = output
        if special_rules is not None and special_rules is not '':
            self.special_rules = []
            extension = '.xml'
            if ',' in special_rules:
                # check rule name
                s_rules = special_rules.split(',')
                for sr in s_rules:
                    if self._check_rule_name(sr):
                        if extension not in sr:
                            sr += extension
                        self.special_rules.append(sr)
                    else:
                        logger.critical('[PARSE-ARGS] Exception rule name: {sr}'.format(sr=sr))
            else:
                if self._check_rule_name(special_rules):
                    if extension not in special_rules:
                        special_rules += extension
                    self.special_rules = [special_rules]
                else:
                    logger.critical(
                        '[PARSE-ARGS] Exception special rule name(e.g: CVI-110001): {sr}'.format(sr=special_rules))
        else:
            self.special_rules = None
        self.sid = a_sid

    @staticmethod
    def _check_rule_name(name):
        return re.match(r'^(cvi|CVI)-\d{6}(\.xml)?', name.strip()) is not None

    @property
    def target_mode(self):
        """
        Parse target mode (git/file/folder/compress)
        :return: str
        """
        target_mode = None
        target_git_cases = ['http://', 'https://', 'ssh://']
        for tgc in target_git_cases:
            if self.target[0:len(tgc)] == tgc:
                target_mode = TARGET_MODE_GIT

        if os.path.isfile(self.target):
            target_mode = TARGET_MODE_FILE
            try:
                if self.target.split('.')[-1] in Config('upload', 'extensions').value.split('|'):
                    target_mode = TARGET_MODE_COMPRESS
            except AttributeError as e:
                logger.critical('Please config the config file copy from the config.template file')
        if os.path.isdir(self.target):
            target_mode = TARGET_MODE_FOLDER
        if target_mode is None:
            logger.critical('[PARSE-ARGS] [-t <target>] can\'t empty!')
            exit()
        logger.debug('[PARSE-ARGS] Target Mode: {mode}'.format(mode=target_mode))
        return target_mode

    @property
    def output_mode(self):
        """
        Parse output mode (api/mail/file/stream)
        :return: str
        """
        output_mode = None
        output_mode_api = ['http', 'https']
        output_mode_mail = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
        if re.match(output_mode_mail, self.output) is not None:
            output_mode = OUTPUT_MODE_MAIL
        for oma in output_mode_api:
            if self.output[0:len(oma)] == oma:
                output_mode = OUTPUT_MODE_API
        if os.path.isdir(os.path.dirname(self.output)):
            output_mode = OUTPUT_MODE_FILE
        if output_mode is None:
            output_mode = OUTPUT_MODE_STREAM
        logger.debug('[PARSE-ARGS] Output Mode: {mode}'.format(mode=output_mode))
        return output_mode

    def target_directory(self, target_mode):
        reg = '^(https?):\/\/[\w\-]+(\.[\w\-:]+)+([\w\-\.?\/]+)?$'
        target_directory = None
        if target_mode == TARGET_MODE_GIT:
            logger.debug('GIT Project')
            # branch or tag
            split_target = self.target.split(':')
            if len(split_target) == 4:
                target, branch = '{p}:{u}:{f}'.format(p=split_target[0], u=split_target[1], f=split_target[2]), \
                                 split_target[-1]
                if re.match(reg, target) is None:
                    logger.critical('Please enter a valid URL')
                    exit()
                branch = pipes.quote(branch)
            if len(split_target) == 3:
                target, branch = '{p}:{u}'.format(p=split_target[0], u=split_target[1]), split_target[-1]
                if '/' in branch:
                    target, branch = '{t}:{b}'.format(t=target, b=branch), 'master'
                if re.match(reg, target) is None:
                    logger.critical('Please enter a valid URL')
                    exit()
                branch = pipes.quote(branch)
            elif len(split_target) == 2:
                target, branch = self.target, 'master'
                if re.match(reg, target) is None:
                    logger.critical('Please enter a valid URL')
                    exit()
                branch = pipes.quote(branch)
            else:
                logger.critical('Target url exception: {u}'.format(u=self.target))
            if 'gitlab' in target:
                username = Config('git', 'username').value
                password = Config('git', 'password').value
            else:
                username = None
                password = None
            gg = Git(repo_address=target, branch=branch, username=username, password=password)

            # Git Clone Error
            try:
                clone_ret, clone_err = gg.clone()
                if clone_ret is False:
                    raise PickupException('Clone Failed ({0})'.format(clone_err), gg)
            except NotExistError:
                raise NotExistException(4001, 'Repository or Branch Does not exist!', gg)
            except AuthError:
                raise AuthFailedException('Git Authentication Failed')
            target_directory = gg.repo_directory
        elif target_mode == TARGET_MODE_COMPRESS:
            ret, target_directory = Decompress(self.target).decompress()
        elif target_mode == TARGET_MODE_FOLDER:
            target_directory = self.target
        elif target_mode == TARGET_MODE_FILE:
            target_directory = self.target
        else:
            logger.critical('[PARSE-ARGS] exception target mode ({mode})'.format(mode=target_mode))
            exit()

        logger.debug('[PARSE-ARGS] target directory: {directory}'.format(directory=target_directory))
        target_directory = os.path.abspath(target_directory)
        if target_directory[-1] == '/':
            return target_directory
        else:
            return u'{t}/'.format(t=target_directory)


def to_bool(value):
    """Converts 'something' to boolean. Raises exception for invalid formats"""
    if str(value).lower() in ("on", "yes", "y", "true", "t", "1"):
        return True
    if str(value).lower() in ("off", "no", "n", "false", "f", "0", "0.0", "", "none", "[]", "{}"):
        return False
    raise Exception('Invalid value for boolean conversion: ' + str(value))


def convert_time(seconds):
    """
    Seconds to minute/second
    Ex: 61 -> 1'1"
    :param seconds:
    :return:
    :link: https://en.wikipedia.org/wiki/Prime_(symbol)
    """
    one_minute = 60
    minute = seconds / one_minute
    if minute == 0:
        return str(seconds % one_minute) + "\""
    else:
        return str(int(minute)) + "'" + str(seconds % one_minute) + "\""


def convert_number(n):
    """
    Convert number to , split
    Ex: 123456 -> 123,456
    :param n:
    :return:
    """
    if n is None:
        return '0'
    n = str(n)
    if '.' in n:
        dollars, cents = n.split('.')
    else:
        dollars, cents = n, None

    r = []
    for i, c in enumerate(str(dollars)[::-1]):
        if i and (not (i % 3)):
            r.insert(0, ',')
        r.insert(0, c)
    out = ''.join(r)
    if cents:
        out += '.' + cents
    return out


def md5(content):
    """
    MD5 Hash
    :param content:
    :return:
    """
    content = content.encode('utf8')
    return hashlib.md5(content).hexdigest()


def allowed_file(filename):
    """
    Allowed upload file
    Config Path: ./config [upload]
    :param filename:
    :return:
    """
    config_extension = Config('upload', 'extensions').value
    if config_extension == '':
        logger.critical('Please set config file upload->directory')
        sys.exit(0)
    allowed_extensions = config_extension.split('|')
    return '.' in filename and filename.rsplit('.', 1)[1] in allowed_extensions


def path_to_short(path, max_length=36):
    """
    /impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java
    /impl/src/.../utils/CertUtil.java
    :param path:
    :param max_length:
    :return:
    """
    if len(path) < max_length:
        return path
    paths = path.split('/')
    paths = filter(None, paths)
    paths = list(paths)
    tmp_path = ''
    for i in range(0, len(paths)):
        logger.debug((i, str(paths[i]), str(paths[len(paths) - i - 1])))
        tmp_path = tmp_path + str(paths[i]) + '/' + str(paths[len(paths) - i - 1])
        if len(tmp_path) > max_length:
            tmp_path = ''
            for j in range(0, i):
                tmp_path = tmp_path + '/' + str(paths[j])
            tmp_path += '/...'
            for k in range(i, 0, -1):
                tmp_path = tmp_path + '/' + str(paths[len(paths) - k])
            if tmp_path == '/...':
                return '.../{0}'.format(paths[len(paths) - 1])
            elif tmp_path[0] == '/':
                return tmp_path[1:]
            else:
                return tmp_path


def path_to_file(path):
    """
    Path to file
    /impl/src/main/java/com/mogujie/service/mgs/digitalcert/utils/CertUtil.java
    .../CertUtil.java
    :param path:
    :return:
    """
    paths = path.split('/')
    paths = list(filter(None, paths))
    length = len(paths)
    return '.../{0}'.format(paths[length - 1])


def percent(part, whole, need_per=True):
    """
    Percent
    :param part:
    :param whole:
    :param need_per:
    :return:
    """
    if need_per:
        per = '%'
    else:
        per = ''
    if part == 0 and whole == 0:
        return 0
    return '{0}{1}'.format(100 * float(part) / float(whole), per)


def timestamp():
    """Get timestamp"""
    return int(time.time())


def format_gmt(time_gmt, time_format=None):
    """
    Format GMT time
    Ex: Wed, 14 Sep 2016 17:57:41 GMT to 2016-09-14 17:57:41
    :param time_gmt:
    :param time_format:
    :return:
    """
    if time_format is None:
        time_format = '%Y-%m-%d %X'
    t = time.strptime(time_gmt, "%a, %d %b %Y %H:%M:%S GMT")
    return time.strftime(time_format, t)


def random_generator(size=6, chars=string.ascii_uppercase + string.digits):
    return ''.join(random.choice(chars) for _ in range(size))


def is_list(value):
    """
    Returns True if the given value is a list-like instance

    >>> is_list([1, 2, 3])
    True
    >>> is_list(u'2')
    False
    """

    return isinstance(value, (list, tuple, set))


def get_unicode(value, encoding=None, none_to_null=False):
    """
    Return the unicode representation of the supplied value:

    >>> get_unicode(u'test')
    u'test'
    >>> get_unicode('test')
    u'test'
    >>> get_unicode(1)
    u'1'
    """

    if none_to_null and value is None:
        return None
    if str(type(value)) == "<class 'bytes'>":
        value = value.encode('utf8')
        return value
    elif str(type(value)) == "<type 'unicode'>":
        return value
    elif is_list(value):
        value = list(get_unicode(_, encoding, none_to_null) for _ in value)
        return value
    else:
        try:
            return value.encode('utf8')
        except UnicodeDecodeError:
            return value.encode('utf8', errors="ignore")


def get_safe_ex_string(ex, encoding=None):
    """
    Safe way how to get the proper exception represtation as a string
    (Note: errors to be avoided: 1) "%s" % Exception(u'\u0161') and 2) "%s" % str(Exception(u'\u0161'))

    >>> get_safe_ex_string(Exception('foobar'))
    u'foobar'
    """

    ret = ex

    if getattr(ex, "message", None):
        ret = ex.message
    elif getattr(ex, "msg", None):
        ret = ex.msg

    return get_unicode(ret or "", encoding=encoding).strip()


def class_to_path(target_projects, class_name):
    """
    转换Java class名为绝对路径，用于跨文件的检测
    :param target_projects: 项目根目录
    :param class_name: import类名
    :return:
    """
    class_path = ''

    if class_name and '.' in class_name:
        class_rpath = class_name.replace('.', '/') + '.java'  # 转换类名为相对路径
    else:
        class_rpath = ''
        logger.warning("[UNTIL] Class_name can't None, False or empty !")

    if target_projects:
        for root, dirs, files in os.walk(target_projects):
            for f in files:
                if f.endswith('.java'):
                    class_new_path = os.path.join(root, f)
                    if class_rpath in class_new_path:
                        class_path = class_new_path

        if class_path != '':
            logger.debug("[UNTIL] The class {c} path {p}".format(c=class_name, p=class_path))
    else:
        logger.warning("[UNTIL] Target_projects can't None, False or empty !")

    return class_path


class Tool:
    def __init__(self):

        # `grep` (`ggrep` on Mac)
        if os.path.isfile('/bin/grep'):
            self.grep = '/bin/grep'
        elif os.path.isfile('/usr/bin/grep'):
            self.grep = '/usr/bin/grep'
        elif os.path.isfile('/usr/local/bin/grep'):
            self.grep = '/usr/local/bin/grep'
        else:
            self.grep = 'grep'

        # `find` (`gfind` on Mac)
        if os.path.isfile('/bin/find'):
            self.find = '/bin/find'
        elif os.path.isfile('/usr/bin/find'):
            self.find = '/usr/bin/find'
        elif os.path.isfile('/usr/local/bin/find'):
            self.find = '/usr/local/bin/find'
        else:
            self.find = 'find'

        if 'darwin' == sys.platform:
            ggrep = ''
            gfind = ''
            for root, dir_names, file_names in os.walk('/usr/local/Cellar/grep'):
                for filename in file_names:
                    if 'ggrep' == filename or 'grep' == filename:
                        ggrep = os.path.join(root, filename)
            for root, dir_names, file_names in os.walk('/usr/local/Cellar/findutils'):
                for filename in file_names:
                    if 'gfind' == filename:
                        gfind = os.path.join(root, filename)
            if ggrep == '':
                logger.critical("brew install grep pleases!")
                sys.exit(0)
            else:
                self.grep = ggrep
            if gfind == '':
                logger.critical("brew install findutils pleases!")
                sys.exit(0)
            else:
                self.find = gfind


def secure_filename(filename):
    _filename_utf8_strip_re = re.compile(u"[^\u4e00-\u9fa5A-Za-z0-9_.\-\+]")
    _windows_device_files = ('CON', 'AUX', 'COM1', 'COM2', 'COM3', 'COM4', 'LPT1', 'LPT2', 'LPT3', 'PRN', 'NUL')

    try:
        text_type = unicode  # Python 2
    except NameError:
        text_type = str  # Python 3

    if isinstance(filename, text_type):
        from unicodedata import normalize
        filename = normalize('NFKD', filename).encode('utf-8', 'ignore')
        if not PY2:
            filename = filename.decode('utf-8')

    if filename in (os.path.sep, os.path.altsep, os.path.pardir):
        return ""

    if PY2:
        filename = filename.decode('utf-8')
    filename = _filename_utf8_strip_re.sub('', '_'.join(filename.split()))

    # on nt a couple of special files are present in each folder.  We
    # have to ensure that the target file is not such a filename.  In
    # this case we prepend an underline
    if os.name == 'nt' and filename and filename.split('.')[0].upper() in _windows_device_files:
        filename = '_' + filename

    return filename


def split_branch(target_str):
    split_target = target_str.split(':')
    if len(split_target) == 3:
        target, branch = '{p}:{u}'.format(p=split_target[0], u=split_target[1]), split_target[-1]
    elif len(split_target) == 2:
        target, branch = target_str, 'master'
    else:
        target, branch = target_str, 'master'

    return target, branch


def unhandled_exception_unicode_message(root, dirs, filenames):
    err_msg = unhandled_exception_message()
    dirs = ','.join(dirs)
    filenames = ','.join(filenames)
    err_msg_unicode = err_msg + """\nRoot path: {rp}\nDirs: {di}\nFilenames: {fn}""".format(
        rp=root,
        di=dirs,
        fn=filenames
    )
    return err_msg_unicode


def unhandled_exception_message():
    """
    Returns detailed message about occurred unhandled exception
    """
    err_msg = """Cobra version: {cv}\nPython version: {pv}\nOperating system: {os}\nCommand line: {cl}""".format(
        cv=__version__,
        pv=__python_version__,
        os=__platform__,
        cl=re.sub(r".+?\bcobra.py\b", "cobra.py", " ".join(sys.argv))
    )
    return err_msg


def create_github_issue(err_msg, exc_msg):
    """
    Automatically create a Github issue with unhandled exception information
    """
    issues = []
    try:
        with open(issue_history_path, 'r') as f:
            for line in f.readlines():
                issues.append(line.strip())
    except:
        pass
    finally:
        # unique
        issues = set(issues)
    _ = re.sub(r"'[^']+'", "''", exc_msg)
    _ = re.sub(r"\s+line \d+", "", _)
    _ = re.sub(r'File ".+?/(\w+\.py)', "\g<1>", _)
    _ = re.sub(r".+\Z", "", _)
    _ = _.encode('utf-8')
    key = hashlib.md5(_).hexdigest()[:8]

    if key in issues:
        logger.warning('issue already reported!')
        return

    ex = None

    try:
        if PY2:  # python2用urllib.quote, python3用urllib.parse.quote
            url = "https://api.github.com/search/issues?q={q}".format(q=urllib.quote("repo:WhaleShark-Team/cobra [AUTO] Unhandled exception (#{k})".format(k=key)))
        else:
            url = "https://api.github.com/search/issues?q={q}".format(q=urllib.parse.quote("repo:WhaleShark-Team/cobra [AUTO] Unhandled exception (#{k})".format(k=key)))
        logger.debug(url)
        resp = requests.get(url=url)
        content = resp.json()
        _ = content
        duplicate = _["total_count"] > 0
        closed = duplicate and _["items"][0]["state"] == "closed"
        if duplicate:
            warn_msg = "issue seems to be already reported"
            if closed:
                warn_msg += " and resolved. Please update to the latest version from official GitHub repository at '{u}'".format(u=__url__)
            logger.warning(warn_msg)
            return
    except:
        logger.warning('search github issue failed')
        pass

    try:
        url = "https://api.github.com/repos/WhaleShark-Team/cobra/issues"
        data = {
            "title": "[AUTO] Unhandled exception (#{k})".format(k=key),
            "body": "## Environment\n```\n{err}\n```\n## Traceback\n```\n{exc}\n```\n".format(err=err_msg, exc=exc_msg)
        }
        headers = {"Authorization": "token {t}".format(t=base64.b64decode(access_token).decode('utf-8'))}
        resp = requests.post(url=url, data=json.dumps(data), headers=headers)
        content = resp.text
    except Exception as ex:
        content = None

    issue_url = re.search(r"https://github.com/WhaleShark-Team/cobra/issues/\d+", content or "")
    if issue_url:
        info_msg = "created Github issue can been found at the address '{u}'".format(u=issue_url.group(0))
        logger.info(info_msg)

        try:
            with open(issue_history_path, "a+b") as f:
                f.write("{k}\n".format(k=key))
        except:
            pass
    else:
        warn_msg = "something went wrong while creating a Github issue"
        if ex:
            warn_msg += " ('{m}')".format(m=get_safe_ex_string(ex))
        if "Unauthorized" in warn_msg:
            warn_msg += ". Please update to the latest revision"
        logger.warning(warn_msg)


def clean_dir(filepath):
    if os.path.isdir(filepath):
        if os.path.isfile(filepath):
            try:
                os.remove(filepath)
            except OSError:
                logger.warning('[RM] remove {} fail'.format(filepath))
        elif os.path.isdir(filepath):
            shutil.rmtree(filepath, True)
    return True


def create_projects_hash():
    """
    用于获取Cobra主要文件的md5值
    :return:
    """
    hash_list = []
    for fi in os.listdir(core_path):  # 遍历所有文件，并记录md5到列表中
        if os.path.splitext(fi)[1] == '.py':
            file_path = os.path.join(core_path, fi)
            with open(file_path, 'r') as file_handler:
                data = file_handler.read()
                md5_data = md5(data)
                hash_list.append(md5_data)

    project_hash = md5(''.join(hash_list))
    return project_hash


def set_config_hash():
    """
    保存项目md5到config文件中
    :return:
    """
    project_hash = create_projects_hash()
    result = Config('hash', 'modified').set(project_hash)  # 修改config文件的MD5，用于本地代码校验

    if result is True:
        logger.info('[HASH] Projects hash save success')
        return True
    return False


def get_config_hash():
    """
    读取项目md5并生成新md5进行比较，相同则项目未改变；否则，项目已被修改
    :return: Bool，True，项目未修改；False，项目已被修改
    """
    new_md5 = create_projects_hash()
    old_md5 = Config('hash', 'modified').value
    if new_md5 == old_md5:
        logger.info('[HASH] Projects is\'t modified')
        return True
    else:
        logger.info('[HASH] Projects is modified')
        return False
