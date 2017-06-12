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
from cobra.utils.config import Config
from cobra.utils.log import logger
from cobra.exceptions import PickupException, NotExistException, AuthFailedException

TARGET_MODE_GIT = 'git'
TARGET_MODE_FILE = 'file'
TARGET_MODE_FOLDER = 'folder'
TARGET_MODE_COMPRESS = 'compress'

OUTPUT_MODE_MAIL = 'mail'
OUTPUT_MODE_API = 'api'
OUTPUT_MODE_FILE = 'file'
OUTPUT_MODE_STREAM = 'stream'


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
        logger.critical('[-t <target>] can\'t empty!')
        exit()
    logger.info('Target Mode: {mode}'.format(mode=target_mode))

    # output mode(api/mail/file/stream)
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
        output_mode = OUTPUT_MODE_STREAM
    logger.info('Output Mode: {mode}'.format(mode=output_mode))

    # target directory
    target_directory = None
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
                raise PickupException('Clone Failed ({0})'.format(clone_err), gg)
        except NotExistError:
            raise NotExistException(4001, 'Repository Does not exist!', gg)
        except AuthError:
            raise AuthFailedException('Git Authentication Failed')
        target_directory = gg.repo_directory
    elif target_mode == TARGET_MODE_COMPRESS:
        from cobra.pickup.compress import support_extensions, Decompress
        extension = target.split('.')[-1]
        if extension not in support_extensions:
            logger.critical('Not support this compress extension: {extension}'.format(extension=extension))
        target_directory = Decompress(target).decompress()
    elif target_mode == TARGET_MODE_FOLDER:
        target_directory = target
    elif target_mode == TARGET_MODE_FILE:
        target_directory = target
    else:
        logger.critical('exception target mode ({mode})'.format(mode=target_mode))
        exit()

    logger.info('target directory: {directory}'.format(directory=target_directory))

    # static analyse files info
    from cobra.pickup import directory
    files, file_count, time_consume = directory.Directory(target_directory).collect_files()

    # detection main language
    main_language = None
    tmp_language = None
    for ext, ext_info in files:
        logger.info("{ext} {count}".format(ext=ext, count=ext_info['count']))
        rules = Config().rule()
        for language, language_info in rules['languages'].items():
            if ext in language_info['extensions']:
                if 'chiefly' in language_info and language_info['chiefly'].lower() == 'true':
                    logger.debug('found the chiefly language({language}), maybe have largest, continue...'.format(language=language))
                    main_language = language
                else:
                    logger.debug('not chiefly, continue...'.format(language=language))
                    tmp_language = language
        if main_language is None:
            logger.debug('not found chiefly language, use the largest language(language) replace'.format(language=tmp_language))
            main_language = tmp_language
    logger.debug('main language({main_language}), tmp language({tmp_language})'.format(tmp_language=tmp_language, main_language=main_language))

    # detection main framework
    from cobra.engine.detection import Framework
    main_framework = Framework(target_directory, main_language).get_framework()

    logger.info("""static analyse
    > main language:    {language}
    > main framework:   {framework}
    > files count:      {files}
    > time consume:     {consume}s
    > extensions count: {ec}
    """.format(
        language=main_language,
        framework=main_framework,
        files=file_count,
        consume=time_consume,
        ec=len(files))
    )

    # vulnerability rules
    from cobra.engine.match import Match
    Match()
