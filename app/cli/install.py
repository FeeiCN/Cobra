#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
    cli.install
    ~~~~~~~~~~~

    Implements CLI install

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/wufeifei/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2017 Feei. All rights reserved
"""
import sys
from sqlalchemy import exc
from flask_script import Command
from utils import common
from app.models import CobraAuth, CobraAdminUser
from app import db


class Install(Command):
    """
    Initialize the table structure
    Usage:
        python cobra.py install
    """

    def run(self):
        # create database structure
        print("Start create database structure...")
        try:
            db.create_all()
        except exc.SQLAlchemyError as e:
            print("MySQL database error: {0}\nFAQ: {1}".format(e, 'http://cobra-docs.readthedocs.io/en/latest/FAQ/'))
            sys.exit(0)
        except Exception as e:
            print(e)
            sys.exit(0)
        print("Create Structure Success.")

        # table `auth`
        print('Insert api key...')
        auth = CobraAuth('manual', common.md5('CobraAuthKey'), 1)
        db.session.add(auth)

        # table `user`
        print('Insert admin user...')
        username = 'admin'
        password = 'admin123456!@#'
        role = 1  # 1: super admin, 2: admin, 3: rules admin
        a_user = CobraAdminUser(username, password, role)
        db.session.add(a_user)

        # commit
        db.session.commit()
        print('All Done.')
