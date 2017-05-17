import os
import re
from utils.log import logger

TARGET_MODE_GIT = 'git'
TARGET_MODE_FILE = 'file'
TARGET_MODE_FOLDER = 'folder'

OUTPUT_MODE_MAIL = 'mail'
OUTPUT_MODE_API = 'api'
OUTPUT_MODE_FILE = 'file'


def start(target, format, output, rule, exclude, debug):
    """
    Start CLI
    :param target: File, FOLDER, GIT
    :param format:
    :param output:
    :param rule:
    :param exclude:
    :param debug:
    :return:
    """
    # target mode
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
    logger.info('Mode: {mode}'.format(mode=target_mode))

    # output mode
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
