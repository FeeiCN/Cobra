import os
import re
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


class ParseArgs(object):
    def __init__(self, target, formatter, output, rule, exclude):
        self.target = target
        self.formatter = formatter
        self.output = output
        self.rule = rule
        self.exclude = exclude

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
        if os.path.isdir(self.target):
            target_mode = TARGET_MODE_FOLDER
        if target_mode is None:
            logger.critical('[-t <target>] can\'t empty!')
            exit()
        logger.info('Target Mode: {mode}'.format(mode=target_mode))
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
        logger.info('Output Mode: {mode}'.format(mode=output_mode))
        return output_mode

    def target_directory(self, target_mode):
        target_directory = None
        if target_mode == TARGET_MODE_GIT:
            from cobra.pickup.git import Git, NotExistError, AuthError
            logger.info('GIT Project')
            branch = 'master'
            username = ''
            password = ''
            gg = Git(self.target, branch=branch, username=username, password=password)

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
            extension = self.target.split('.')[-1]
            if extension not in support_extensions:
                logger.critical('Not support this compress extension: {extension}'.format(extension=extension))
            target_directory = Decompress(self.target).decompress()
        elif target_mode == TARGET_MODE_FOLDER:
            target_directory = self.target
        elif target_mode == TARGET_MODE_FILE:
            target_directory = self.target
        else:
            logger.critical('exception target mode ({mode})'.format(mode=target_mode))
            exit()

        logger.info('target directory: {directory}'.format(directory=target_directory))
        return target_directory
