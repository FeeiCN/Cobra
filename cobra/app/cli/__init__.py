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
from cobra.pickup import directory
from cobra.app.cli.parseargs import ParseArgs
from cobra.engine.detection import Detection
from cobra.engine.rules import Rules
from cobra.utils.log import logger


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

    # init rules data
    r = Rules()
    vulnerabilities = r.vulnerabilities
    languages = r.languages
    frameworks = r.frameworks
    rules = r.rules

    # static analyse files info
    files, file_count, time_consume = directory.Directory(target_directory).collect_files()

    # detection main language and framework
    dt = Detection(target_directory, files)
    main_language = dt.language
    main_framework = dt.framework

    logger.info("""static analyse
    > Target: {target} Output: {output}
    > directory: {directory}
    > main language:    {language}
    > main framework:   {framework}
    > files count:      {files}
    > time consume:     {consume}s
    > extensions count: {ec}
    """.format(
        directory=target_directory,
        target=target_mode,
        output=output_mode,
        language=main_language,
        framework=main_framework,
        files=file_count,
        consume=time_consume,
        ec=len(files))
    )

    # scan
    pass
