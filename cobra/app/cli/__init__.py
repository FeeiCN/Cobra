# -*- coding: utf-8 -*-

"""
    app.cli
    ~~~~~~~

    Implements app cli

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import os
import re
from cobra.utils.log import logger
from cobra.engine.static import Static

TARGET_MODE_GIT = 'git'
TARGET_MODE_FILE = 'file'
TARGET_MODE_FOLDER = 'folder'
TARGET_MODE_COMPRESS = 'compress'

OUTPUT_MODE_MAIL = 'mail'
OUTPUT_MODE_API = 'api'
OUTPUT_MODE_FILE = 'file'


def start(target, format, output, rule, exclude):
    """
    Start CLI
    :param target: File, FOLDER, GIT
    :param format:
    :param output:
    :param rule:
    :param exclude:
    :return:
    """
    # target mode(git/folder/file)
    target_mode = None
    target_git_cases = ['http://', 'https://', 'ssh://']
    for tgc in target_git_cases:
        if target[0:len(tgc)] == tgc:
            target_mode = TARGET_MODE_GIT

    if os.path.isfile(target):
        target_mode = TARGET_MODE_FILE
    if os.path.isdir(target):
        target_mode = TARGET_MODE_FOLDER
    if target_mode is None:
        logger.critical('<target> not support!')
        exit()
    logger.info('Target Mode: {mode}'.format(mode=target_mode))

    # output mode(api/mail/file)
    output_mode = None
    output_mode_api = ['http', 'https']
    output_mode_mail = r"(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)"
    if re.match(output_mode_mail, output) is not None:
        output_mode = OUTPUT_MODE_MAIL
    for oma in output_mode_api:
        if output[0:len(oma)] == oma:
            output_mode = OUTPUT_MODE_API
    if os.path.isdir(os.path.dirname(output)):
        output_mode = OUTPUT_MODE_FILE
    if output_mode is None:
        logger.critical('<output> not support!')
        exit()
    logger.info('Output Mode: {mode}'.format(mode=output_mode))

    if target_mode == TARGET_MODE_GIT:
        from cobra.pickup.git import Git, NotExistError, AuthError
        logger.info('GIT Project')
        branch = 'master'
        username = ''
        password = ''
        gg = Git(target, branch=branch, username=username, password=password)

        # Git Clone Error
        try:
            clone_ret, clone_err = gg.clone()
            if clone_ret is False:
                logger.critical(4001, 'Clone Failed ({0})'.format(clone_err), gg)
                exit()
        except NotExistError:
            logger.critical(4001, 'Repository Does not exist!', gg)
            exit()
        except AuthError:
            logger.critical('Git Authentication Failed')
            exit()
        directory = gg.repo_directory
    elif target_mode == TARGET_MODE_COMPRESS:
        from cobra.pickup.compress import support_extensions, Decompress
        extension = target.split('.')[-1]
        if extension not in support_extensions:
            logger.critical('Not support this compress extension: {extension}'.format(extension=extension))
        directory = Decompress(target).decompress()

    logger.info('target directory: {directory}'.format(directory=directory))

