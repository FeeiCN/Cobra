import os
import logging

logging = logging.getLogger(__name__)

TARGET_MODE_GIT = 'git'
TARGET_MODE_FILE = 'file'
TARGET_MODE_FOLDER = 'folder'


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
        logging.critical('<target> not support!')
        exit()

    logging.info('Mode: {mode}'.format(mode=target_mode))
