#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/edge-security/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#

import os
import subprocess
from urllib import quote

from utils import log

"""
usage and example.

#!/usr/bin/env python
from pickup.GitTools import Git
repo_address = 'your repo address here'

# create a git object.
gg = Git(repo_address, 'your username here', 'your password here')

# use get_repo() method to clone the repo, if already cloned, it will pull the latest version.
gg.get_repo()

# you can also call the special method manually.
# clone() will clone the repo to local.
# pull() will pull the local repo to the latest version.
# gg.clone()
# gg.pull()

# diff(new_version, old_version) method will diff the two version.
# and return the diff result in str.
diff_result = gg.diff('ef8ab030a54e3', '4640bc08a08f4')
print diff_result
"""


class Git:
    """
    A Git class.
    You can clone, pull, diff the repo via this class.

    repo_address: the repo's url
    repo_directory: the repo's local path
    repo_username: the username for the repo's url
    repo_password: the password for the repo's password
    """

    repo_address = None
    repo_directory = None
    repo_username = None
    repo_password = None

    # https://github.com/<username>/<reponame>

    def __init__(self, repo_address, username, password):
        self.repo_address = repo_address
        self.repo_username = username
        self.repo_password = password
        repo_user = self.repo_address.split('/')[-2]
        repo_name = self.repo_address.split('/')[-1]
        if '.git' not in repo_name:
            self.repo_address += '.git'
        else:
            repo_name = repo_name.split('.')[0]

        self.repo_directory = 'uploads/' + repo_user + '_' + repo_name

        log.info('Git class init.')

    def pull(self):
        """Pull a repo from repo_address and repo_directory"""
        log.info('start pull repo')

        # change work directory to the repo
        current_dir = os.getcwd() + os.sep
        repo_dir = current_dir + self.repo_directory
        os.chdir(repo_dir)

        cmd = 'git pull'
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (pull_out, pull_err) = p.communicate()
        log.info(pull_out)

        # change work directory back.
        os.chdir(current_dir)
        log.info('pull done.')

    def clone(self):
        """Clone a repo from repo_address"""
        log.info('start clone repo')
        clone_address = self.repo_address.split('://')[0] + '://' + self.repo_username + '@' + \
                        self.repo_address.split('://')[1]

        # clone repo with username and password
        # "http[s]://username:password@gitlab.com/username/reponame"
        # if add password in the url, .git/config will log your url with password
        # so only set username in the url, and echo password to "git clone"
        # "echo password | git clone http[s]://username@gitlab.com/username/reponame"
        cmd = 'echo ' + quote(self.repo_password) + ' | ' + 'git clone ' + \
              clone_address + ' "' + self.repo_directory + '"'

        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (clone_out, clone_err) = p.communicate()
        log.info(clone_err)
        log.info('clone done.')

    def diff(self, new_version, old_version):
        """
        Diff between two version, in SHA hex.
        :param new_version: the new version in SHA hex.
        :param old_version: the old version in SHA hex.
        :return: the diff result in str.
        """

        # change the work directory to the repo.
        current_dir = os.getcwd() + os.sep
        repo_dir = current_dir + self.repo_directory
        os.chdir(repo_dir)

        cmd = 'git diff ' + old_version + ' ' + new_version
        p = subprocess.Popen(cmd, shell=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        (diff_out, diff_err) = p.communicate()
        log.info(diff_out)

        # change the work directory back.
        os.chdir(current_dir)
        log.info('diff done.')

        return diff_out

    def __check_exist(self):
        """check if the repo has already cloned.
        :returns bool
            true : the repo already exist.
            false : the repo do not exist.
        """
        if os.path.isdir(self.repo_directory):
            return True
        else:
            return False

    def get_repo(self):
        """
        clone or pull the special repo.
        If the repo already exist in the "uploads" folder, it will pull the repo.
        If there is no repo in "uploads" folder, it will clone the repo.
        :return:
        """
        if self.__check_exist():
            log.info('repo already exist. Try to pull the repo')
            self.pull()
        else:
            self.clone()

    def __repr__(self):
        return "<Git - %r@%r>" % (self.repo_username, self.repo_address)
