# -*- coding: utf-8 -*-

"""
    utils.decompress
    ~~~~~~~~~~~~~~~~

    Implements decompress file

    :author:    Feei <wufeifei#wufeifei.com>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2016 Feei. All rights reserved
"""
import os
import shutil
import zipfile
import tarfile
import rarfile
from utils import config, log

"""example

Decompress a compressed file.
It will store the file in the "uploads/filename/" directory.
for example, if there is a file named "111_test.rar" in uploads dir, after decompress,
it will create a directory named "111_test"

# import class
from utils.decompress import Decompress

# load an compressed file. only tar.gz, rar, zip supported.
dc = Decompress('222_test.tar.gz')
# decompress it. And there will create a directory named "222_test.tar".
dc.decompress()
"""


class Decompress:
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
        self.upload_directory = os.path.join(config.Config('upload', 'directory').value, 'uploads')
        self.filename = filename
        self.filepath = os.path.join(self.upload_directory, filename)
        self.dir_name = os.path.splitext(self.filename)[0]

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
        directory = os.path.join(self.upload_directory, self.dir_name)
        file_count = 0
        directory_path = None
        for filename in os.listdir(directory):
            directory_path = os.path.join(directory, filename)
            file_count += 1
        log.info("Decompress path count: {0}, directory path: {1}".format(file_count, directory_path))
        if file_count == 1 and os.path.isdir(directory_path):
            return directory_path
        else:
            return directory

    def __decompress_zip(self):
        """unzip a file."""
        zip_file = zipfile.ZipFile(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        # create the file directory to store the extract file.
        os.mkdir(os.path.join(self.upload_directory, self.dir_name))

        zip_file.extractall(os.path.join(self.upload_directory, self.dir_name))
        zip_file.close()

        return True

    def __decompress_rar(self):
        """extract a rar file."""
        rar_file = rarfile.RarFile(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        os.mkdir(os.path.join(self.upload_directory, self.dir_name))

        rar_file.extractall(os.path.join(self.upload_directory, self.dir_name))
        rar_file.close()
        return True

    def __decompress_tar_gz(self):
        """extract a tar.gz file"""
        tar_file = tarfile.open(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        os.mkdir(os.path.join(self.upload_directory, self.dir_name))

        tar_file.extractall(os.path.join(self.upload_directory, self.dir_name))
        tar_file.close()
        return True

    def __check_filename_dir(self):
        if os.path.isdir(os.path.join(self.upload_directory, self.dir_name)):
            shutil.rmtree(os.path.join(self.upload_directory, self.dir_name))

    def __repr__(self):
        return "<decompress - %r>" % self.filename
