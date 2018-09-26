# -*- coding: utf-8 -*-

"""
    pickup
    ~~~~~~

    Implements pickup git/compress file

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""
import os
import re
import sys
import time
import shutil
import zipfile
import tarfile
import rarfile
import subprocess
from . import config
from .log import logger
from .config import package_path, source_path
from shutil import copyfile
from werkzeug.utils import secure_filename
from zipfile import BadZipfile
from rarfile import NotRarFile, BadRarFile
from tarfile import ReadError

try:
    from urllib import quote
except ImportError:
    from urllib.parse import quote


class Decompress(object):
    """Decompress zip, rar and tar.gz

    filename: filename without path
    filetype: file type display in MIME type.
    filepath: filename with path

    """

    filename = None
    filetype = None
    filepath = None

    def __init__(self, filename):
        """
        :param filename: a file name without path.
        """
        self.package_path = package_path
        self.filepath = os.path.join(package_path, secure_filename(filename))
        self.filename = filename
        copyfile(os.path.abspath(filename), self.filepath)
        self.dir_name = secure_filename(filename).split('.')[0]
        print(self.dir_name)

    def decompress(self):
        """
        Decompress a file.
        :return: a dict.
            code: -1 -> error, 1-> success
            msg: None or error message
            dir_name: decompressed directory name. Usually, the directory name is the filename without file extension.
        """

        if '.zip' in self.filename:
            return self.__decompress_zip(), self.get_real_directory()
        elif '.rar' in self.filename:
            return self.__decompress_rar(), self.get_real_directory()
        elif '.tgz' in self.filename or '.tar' in self.filename or '.gz' in self.filename:
            """
            Support Tar Extension
            .tar: .tar | .tar.gz | .tar.bz2
            .gz
            .tgz
            """
            return self.__decompress_tar_gz(), self.get_real_directory()
        else:
            return False, 'File type error, only zip, rar, tar.gz accepted.'

    def get_real_directory(self):
        """
        get real directory
        /path/project-v1.2/project-v1.2 -> /path/project-v1.2/
        :param:
        :return:
        """
        directory = os.path.join(self.package_path, self.dir_name)
        file_count = 0
        directory_path = None
        for filename in os.listdir(directory):
            directory_path = os.path.join(directory, filename)
            file_count += 1
        logger.info("Decompress path count: {0}, directory path: {1}".format(file_count, directory_path))
        if file_count == 1 and os.path.isdir(directory_path):
            return directory_path
        else:
            return directory

    def __decompress_zip(self):
        """unzip a file."""
        try:
            zip_file = zipfile.ZipFile(self.filepath)
            # check if there is a filename directory
            self.__check_filename_dir()

            # create the file directory to store the extract file.
            os.mkdir(os.path.join(self.package_path, self.dir_name))

            zip_file.extractall(os.path.join(self.package_path, self.dir_name))
            zip_file.close()
        except BadZipfile:
            logger.error('File is not a zip file or is bad zip file')
            exit()

        return True

    def __decompress_rar(self):
        """extract a rar file."""
        try:
            rar_file = rarfile.RarFile(self.filepath)
            # check if there is a filename directory
            self.__check_filename_dir()

            os.mkdir(os.path.join(self.package_path, self.dir_name))

            rar_file.extractall(os.path.join(self.package_path, self.dir_name))
            rar_file.close()
        except (BadRarFile, NotRarFile):
            logger.error('File is not a rar file or is bad rar file')
            exit()

        return True

    def __decompress_tar_gz(self):
        """extract a tar.gz file"""
        try:
            tar_file = tarfile.open(self.filepath)
            # check if there is a filename directory
            self.__check_filename_dir()

            os.mkdir(os.path.join(self.package_path, self.dir_name))

            tar_file.extractall(os.path.join(self.package_path, self.dir_name))
            tar_file.close()
        except ReadError:
            logger.error('File is not a tar file or is bad tar file')
            exit()

            return True

    def __check_filename_dir(self):
        if os.path.isdir(os.path.join(self.package_path, self.dir_name)):
            shutil.rmtree(os.path.join(self.package_path, self.dir_name))

    def __repr__(self):
        return "<decompress - %r>" % self.filename


class Directory(object):
    def __init__(self, absolute_path):
        self.absolute_path = absolute_path

    file_sum = 0
    type_nums = {}
    result = {}
    file = []

    """
    :return {'.php': {'count': 2, 'list': ['/path/a.php', '/path/b.php']}}, file_sum, time_consume
    """

    def collect_files(self):
        t1 = time.clock()
        self.files(self.absolute_path)
        self.result['no_extension'] = {'count': 0, 'list': []}
        for extension, values in self.type_nums.items():
            extension = extension.strip()
            self.result[extension] = {'count': len(values), 'list': []}
            # .php : 123
            logger.debug('[PICKUP] [EXTENSION-COUNT] {0} : {1}'.format(extension, len(values)))
            for f in self.file:
                es = f.split(os.extsep)
                if len(es) >= 2:
                    # Exists Extension
                    # os.extsep + es[len(es) - 1]
                    if f.endswith(extension):
                        self.result[extension]['list'].append(f)
                else:
                    # Didn't have extension
                    self.result['no_extension']['count'] = int(self.result['no_extension']['count']) + 1
                    self.result['no_extension']['list'].append(f)
        if self.result['no_extension']['count'] == 0:
            del self.result['no_extension']
        t2 = time.clock()
        # reverse list count
        self.result = sorted(self.result.items(), key=lambda t: t[0], reverse=False)
        return self.result, self.file_sum, t2 - t1

    def files(self, absolute_path, level=1):
        if level == 1:
            logger.debug('[PICKUP] ' + absolute_path)
        try:
            if os.path.isfile(absolute_path):
                filename, directory = os.path.split(absolute_path)
                self.file_info(directory, filename)
            else:
                for filename in os.listdir(absolute_path):
                    if self.is_pickup_whitelist(filename):
                        continue
                    else:
                        try:
                            directory = os.path.join(absolute_path, filename)
                        except UnicodeDecodeError as e:
                            logger.debug('Exception unicode {e}'.format(e=e))
                            continue

                    # Directory Structure
                    logger.debug('[PICKUP] [FILES] ' + '|  ' * (level - 1) + '|--' + filename)
                    if os.path.isdir(directory):
                        self.files(directory, level + 1)
                    if os.path.isfile(directory):
                        self.file_info(directory, filename)
        except OSError as e:
            logger.critical('[PICKUP] {msg}'.format(msg=e))
            exit()

    def is_pickup_whitelist(self, filename):
        whitelist = [
            'node_modules',
            'vendor',
        ]
        if filename in whitelist:
            return True
        else:
            return False

    def file_info(self, path, filename):
        # Statistic File Type Count
        file_name, file_extension = os.path.splitext(path)
        self.type_nums.setdefault(file_extension.lower(), []).append(filename)

        path = path.replace(self.absolute_path, '')
        self.file.append(path)
        self.file_sum += 1


class File(object):
    def __init__(self, file_path):
        self.file_path = file_path

    def read_file(self):
        """
        读取文件内容
        :return:
        """
        f = open(self.file_path, 'r').read()
        return f

    def lines(self, line_rule):
        """
        获取指定行内容
        :param line_rule:
        :return:
        """
        param = ['sed', "-n", line_rule, self.file_path]
        p = subprocess.Popen(param, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
        result, err = p.communicate()
        if len(err) is not 0:
            logger.critical('[PICKUP] {err}'.format(err=err.strip()))
        if len(result):
            try:
                content = result.decode('utf-8')
            except AttributeError as e:
                content = result
            if content == '':
                content = False
        else:
            content = False
        return content


class GitError(Exception):
    def __init__(self, message):
        Exception.__init__(self)
        self.message = message

    def __str__(self):
        return repr(self.message)


class NotExistError(GitError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class AuthError(GitError):
    def __init__(self, message):
        self.message = message

    def __str__(self):
        return repr(self.message)


class Git(object):
    """
    A Git class.
    You can clone, pull, diff the repo via this class.

    repo_address: the repo's url
    repo_directory: the repo's local path
    repo_username: the username for the repo's url
    repo_password: the password for the repo's password
    repo_branch: the repo branch
    """

    repo_address = None
    repo_directory = None
    repo_username = None
    repo_password = None
    repo_branch = None
    repo_author = None
    repo_name = None

    # https://github.com/<username>/<reponame>

    def __init__(self, repo_address, branch='master', username=None, password=None):

        # get upload directory
        self.upload_directory = source_path
        if os.path.isdir(self.upload_directory) is False:
            os.makedirs(self.upload_directory)

        self.repo_address = repo_address
        self.repo_username = username
        self.repo_password = password
        self.repo_branch = branch
        repo_user = self.repo_address.split('/')[-2]
        repo_name = self.repo_address.split('/')[-1].replace('.git', '')
        self.repo_author = repo_user
        self.repo_name = repo_name

        self.repo_directory = os.path.join(os.path.join(self.upload_directory, repo_user), repo_name)

    def pull(self):
        """Pull a repo from repo_address and repo_directory"""
        logger.info('[PICKUP] [PULL] pull repository...')

        if not self.__check_exist():
            return False, 'No local repo exist. Please clone first.'

        # change work directory to the repo
        repo_dir = self.repo_directory
        logger.debug('[PICKUP] cd directory: {0}'.format(repo_dir))
        os.chdir(repo_dir)

        if not self.checkout(self.repo_branch):
            os.chdir(repo_dir)
            return False, "Checkout failed."

        cmd = 'git pull origin ' + self.repo_branch
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        pull_out, pull_err = p.communicate()

        try:
            pull_out = pull_out.decode('utf-8')
            pull_err = pull_err.decode('utf-8')
        except AttributeError as e:
            pass

        logger.info('[PICKUP] [PULL] {o}'.format(o=pull_out.strip()))
        logger.info('[PICKUP] [PULL] {e}'.format(e=pull_err.strip().replace(u'\n', u' >')))

        self.parse_err(pull_err)

        pull_err = pull_err.replace('{0}:{1}'.format(self.repo_username, self.repo_password), '')

        # change work directory back.
        os.chdir(repo_dir)
        pull_out = pull_out.lower()
        if 'up' in pull_out and 'to' in pull_out and 'date' in pull_out:
            logger.info('[PICKUP] [PULL] pull done.')
            return True, None
        else:
            return False, pull_err

    def clone(self):
        """Clone a repo from repo_address
        :return: True - clone success, False - clone error.
        """
        logger.info('[PICKUP] [CLONE] clone repository...')
        if self.__check_exist():
            logger.info('[PICKUP] [CLONE] repository already exist.')
            return self.pull()
            # call(['rm', '-rf', self.repo_directory])

        # if no username or password provide, it may be a public repo.
        if self.repo_username is None or self.repo_password is None:
            # public repo
            clone_address = self.repo_address
        else:
            # private repo
            clone_address = self.repo_address.split('://')[0] + '://' + quote(self.repo_username) + ':' + \
                            quote(self.repo_password) + '@' + self.repo_address.split('://')[1]
        # clone repo with username and password
        # "http[s]://username:password@gitlab.com/username/reponame"
        # !!! if add password in the url, .git/config will log your url with password
        cmd = 'git clone ' + clone_address + ' "' + self.repo_directory + '" -b ' + self.repo_branch

        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (clone_out, clone_err) = p.communicate()

        clone_out = clone_out.decode('utf-8')
        clone_err = clone_err.decode('utf-8')

        clone_err = clone_err.replace('{0}:{1}'.format(self.repo_username, self.repo_password), '')

        logger.debug('[PICKUP] [CLONE] ' + clone_out.strip())
        logger.info('[PICKUP] [CLONE] ' + clone_err.strip())

        self.parse_err(clone_err)

        logger.info('[PICKUP] [CLONE] clone done. Switching to branch ' + self.repo_branch)
        # check out to special branch
        if self.checkout(self.repo_branch):
            return True, None
        else:
            return False, clone_err

    def diff(self, new_version, old_version, raw_output=False):
        """
        Diff between two version, in SHA hex.
        :param new_version: the new version in SHA hex.
        :param old_version: the old version in SHA hex.
        :param raw_output: True-return raw git diff result, False-return parsed result, only add content
        :return: the diff result in str, raw or formatted.
        """
        if not self.__check_exist():
            logger.info('No local repo exist. Please clone it first.')
            return False

        # change the work directory to the repo.
        current_dir = os.getcwd() + os.sep
        repo_dir = current_dir + self.repo_directory
        os.chdir(repo_dir)

        cmd = 'git diff ' + old_version + ' ' + new_version
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (diff_out, diff_err) = p.communicate()

        diff_out = diff_out.decode('utf-8')
        diff_err = diff_err.decode('utf-8')

        logger.info(diff_out)

        # change the work directory back.
        os.chdir(current_dir)
        logger.info('diff done.')
        if raw_output:
            return diff_out
        else:
            return self.__parse_diff_result(diff_out)

    def checkout(self, branch):
        """
        Checkout to special branch.
        :param branch: branch name
        :return: True-checkout success or already on special branch
                 False-checkout failed. Maybe no branch name.
        """
        if not self.__check_exist():
            logger.info('[PICKUP] No repo directory.')
            return False

        current_dir = os.getcwd()
        os.chdir(self.repo_directory)

        cmd = "git fetch origin && git reset --hard origin/{branch} && git checkout {branch}".format(branch=branch)
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (checkout_out, checkout_err) = p.communicate()

        checkout_out = checkout_out.decode('utf-8')
        checkout_err = checkout_err.decode('utf-8')

        logger.info('[PICKUP] [CHECKOUT] ' + checkout_err.strip())

        # Already on
        # did not match
        # Switched to a new branch
        if 'did not match' in checkout_err:
            os.chdir(current_dir)
            return False
        else:
            os.chdir(current_dir)
            return True

    def __check_exist(self):
        """check if the repo has already cloned.
        :returns bool
            True : the repo already exist.
            False : the repo do not exist.
        """
        if os.path.isdir(self.repo_directory):
            return True
        else:
            return False

    @staticmethod
    def __parse_diff_result(content):
        """parse git diff output, return the format result
        :return: a dict, each key is the filename which has changed.
                 each value is a list store every changes.
        example:
                {'bb.txt': ['hhhhhhh'], 'aa.txt': ['ccccc', 'ddddd']}
                bb.txt add a line, the content is 'hhhhhhh'.
                aa.txt add two line, the content is 'ccccc' and 'ddddd'.
        """
        result = {}
        content = content.split('\n')
        tmp_filename = ''
        for x in content:
            if x != '' and x[0:3] == '+++':
                tmp_filename = x.split('/')[-1]
                result[tmp_filename] = []
            elif x != '' and x[0] == '+':
                if x[1:] != '':
                    result[tmp_filename].append(x[1:])

        return result

    def get_repo(self):
        """
        clone or pull the special repo.
        If the repo already exist in the "uploads" folder, it will pull the repo.
        If there is no repo in "uploads" folder, it will clone the repo.
        :return:
        """
        if self.__check_exist():
            logger.info('repo already exist. Try to pull the repo')
            return self.pull()
        else:
            return self.clone()

    @staticmethod
    def parse_err(err):
        if 'not found' in err or 'Not found' in err:
            raise NotExistError('Repo doesn\'t exist')
        elif 'already exists' in err:
            return False, 'repo has already cloned.'
        elif 'Authentication failed' in err:
            raise NotExistError('Authentication failed')

    @staticmethod
    def committer(directory, file_path, line_number, length=1):
        """
        git blame -L21,+1 -- git.py
        362d5798 (wufeifei 2016-09-10 12:19:44 +0800 21) logging = logger.getLogger(__name__)
        (?:.{8}\s\()(.*)\s(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})
        group #1: wufeifei
        group #2: 2016-09-10 12:19:44
        :param directory:
        :param file_path:
        :param line_number:
        :param length:
        :return: group#1, group#2
        """
        if os.path.isdir(directory):
            os.chdir(directory)
        cmd = "git blame -L{0},+{1} -- {2}".format(line_number, length, file_path.replace(directory, ''))
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        checkout_out, checkout_err = p.communicate()
        try:
            checkout_out = checkout_out.decode('utf-8')
        except AttributeError as e:
            pass
        if len(checkout_out) != 0:
            group = re.findall(r'(?:.{8}\s\()(.*)\s(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2})', checkout_out)
            if len(group) > 0:
                return True, group[0][0], group[0][1]
            else:
                return False, None, None
        else:
            return False, None, None

    def __repr__(self):
        return "<Git - %r@%r>" % (self.repo_username, self.repo_address)


class Subversion(object):
    """Subversion Utility Class"""
    svn = '/usr/bin/svn'

    def __init__(self, filename, current_version=None, online_version=None):
        self.filename = filename
        self.current_version = current_version
        self.online_version = online_version

        self.username = config.Config('svn', 'username').value
        self.password = config.Config('svn', 'password').value

        # Test SVN
        cmd = self.svn + " info --no-auth-cache --non-interactive --username='%s' --password='%s' %s" % (
            self.username,
            self.password,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (diff_out, diff_err) = p.communicate()

        diff_out = diff_out.decode('utf-8')
        diff_err = diff_err.decode('utf-8')

        if len(diff_err) == 0:
            logger.debug("[PICKUP] svn diff success")
        elif 'authorization failed' in diff_err:
            logger.warning("svn diff auth failed")
            sys.exit(1)
        elif 'Not a valid URL' in diff_err:
            logger.warning("[PICKUP] svn diff url not a valid")
            sys.exit(1)

    def log(self):
        cmd = self.svn + " log --no-auth-cache --non-interactive --username='%s' --password='%s' %s" % (
            self.username,
            self.password,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        log_out = p.communicate()[0]
        log_out = log_out.decode('utf-8')

        return log_out

    def diff(self):
        cmd = self.svn + " diff --no-auth-cache --non-interactive --username='%s' --password='%s' -r %s:%s %s" % (
            self.username,
            self.password,
            self.current_version,
            self.online_version,
            self.filename
        )
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        diff_out = p.communicate()[0]
        diff_out = diff_out.decode('utf-8')

        added, removed, changed = [], [], []
        diff = {}
        for line in diff_out.split("\n"):
            if line[:3] in ('---', '+++', '==='):
                continue
            else:
                if len(line) > 0:
                    diff.setdefault(line[0], []).append(line[1:].strip())
                    if line[0] == '-':
                        removed.append(line[1:].strip())
                    elif line[0] == '+':
                        added.append(line[1:].strip())
                    elif line[0] == ' ':
                        changed.append(line[1:].strip())
                    else:
                        continue
        diff['code'] = diff_out
        return diff

    def commit(self):
        svn_log = subprocess.Popen(
            [self.svn, 'log', self.filename],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE).communicate()[0]
        return svn_log
