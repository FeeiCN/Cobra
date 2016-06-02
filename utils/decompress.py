#!/usr/bin/env python
#
# Copyright 2016 Feei. All Rights Reserved
#
# Author:   Feei <wufeifei@wufeifei.com>
# Homepage: https://github.com/wufeifei/cobra
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.
#
# See the file 'doc/COPYING' for copying permission
#
import os
import shutil
import zipfile
import tarfile
import ConfigParser

import rarfile
import magic


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
        config = ConfigParser.ConfigParser()
        config.read('config')
        self.upload_directory = config.get('cobra', 'upload_directory') + os.sep
        self.filename = filename
        self.filepath = self.upload_directory + filename
        self.filetype = magic.from_file(self.filepath, mime=True)
        self.dir_name = os.path.splitext(self.filename)[0]

    def decompress(self):
        """
        Decompress a file.
        :return: a dict.
            code: -1 -> error, 1-> success
            msg: None or error message
            dir_name: decompressed directory name. Usually, the directory name is the filename without file extension.
        """
        if self.filetype == 'application/zip':
            return self.__decompress_zip()
        elif self.filetype == 'application/x-rar':
            return self.__decompress_rar()
        elif self.filetype == 'application/x-gzip':
            return self.__decompress_tar_gz()
        else:
            return {'code': -1, 'msg': u'File type error, only zip, rar, tar.gz accepted.'}

    def get_file_type(self):
        return self.filetype

    def __decompress_zip(self):
        """unzip a file."""
        zip_file = zipfile.ZipFile(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        # create the file directory to store the extract file.
        os.mkdir(self.upload_directory + self.dir_name)

        zip_file.extractall(self.upload_directory + self.dir_name)
        zip_file.close()

        return {'code': 1, 'msg': u'Success', 'dir_name': self.dir_name}

    def __decompress_rar(self):
        """extract a rar file."""
        rar_file = rarfile.RarFile(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        os.mkdir(self.upload_directory + self.dir_name)

        rar_file.extractall(self.upload_directory + self.dir_name)
        rar_file.close()

        return {'code': 1, 'msg': u'Success', 'dir_name': self.dir_name}

    def __decompress_tar_gz(self):
        """extract a tar.gz file"""
        tar_file = tarfile.open(self.filepath)
        # check if there is a filename directory
        self.__check_filename_dir()

        os.mkdir(self.upload_directory + self.dir_name)

        tar_file.extractall(self.upload_directory + self.dir_name)
        tar_file.close()

        return {'code': 1, 'msg': u'Success', 'dir_name': self.dir_name}

    def __check_filename_dir(self):
        if os.path.isdir(self.upload_directory + self.dir_name):
            shutil.rmtree(self.upload_directory + self.dir_name)

    def __repr__(self):
        return "<decompress - %r>" % self.filename


