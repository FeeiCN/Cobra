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
from pickup import directory
# from engine import static


class Scan:
    target_files = {}

    def __init__(self, project_path):
        self.project_path = project_path

    # def vul(self, extensions, val_types):
    #     target_files = self.files()
    #
    #     # Detection Developer Language
    #     if ".php" in target_files and ".java" not in target_files:
    #         language = 'php'
    #     elif ".php" not in target_files and ".java" in target_files:
    #         language = 'java'
    #     elif ".php" in target_files and ".java" in target_files:
    #         if target_files[".php"] > target_files['.java']:
    #             language = 'php'
    #         else:
    #             language = 'java'
    #     elif ".php" not in target_files and ".java" not in target_files:
    #         print("Not support the language")
    #
    #     # s = static.Static(language)
    #     static.Static(extensions).analyse()
    #
    #     for ext in extensions:
    #         # {'file_count': 1, 'file_list': []}
    #         target_files_ext = target_files[ext]

    def files(self):
        d = directory.Directory(self.project_path)
        self.target_files = d.collect_files()
        return self.target_files
