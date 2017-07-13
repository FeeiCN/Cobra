# -*- coding: utf-8 -*-

"""
    cli
    ~~~

    Implements CLI mode

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
from .pickup import Directory
from .utils import ParseArgs
from .engine import Detection
from .engine import scan
from .log import logger


def start(target, formatter, output, rule, exclude):
    """
    Start CLI
    :param target: File, FOLDER, GIT
    :param formatter:
    :param output:
    :param rule:
    :param exclude:
    :return:
    """
    # parse target mode and output mode
    pa = ParseArgs(target, formatter, output, rule, exclude)
    target_mode = pa.target_mode
    output_mode = pa.output_mode

    # target directory
    target_directory = pa.target_directory(target_mode)

    # static analyse files info
    files, file_count, time_consume = Directory(target_directory).collect_files()

    # detection main language and framework
    dt = Detection(target_directory, files)
    main_language = dt.language
    main_framework = dt.framework

    logger.info('Static analysis')
    logger.info(' > Target: {tm}, Output: {om}'.format(tm=target_mode, om=output_mode))
    logger.info(' > {d}'.format(d=target_directory))
    logger.info(' > Language: {l}, Framework: {f}'.format(l=main_language, f=main_framework))
    logger.info(' > Files: {fc}, Extensions:{ec}, Consume: {tc}'.format(fc=file_count, ec=len(files), tc=time_consume))

    # scan
    scan(target_directory)
