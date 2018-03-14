# -*- coding: utf-8 -*-

"""
    exceptions
    ~~~~~~~~~~

    Implements exceptions

    :author:    Feei <feei@feei.cn>
    :homepage:  https://github.com/WhaleShark-Team/cobra
    :license:   MIT, see LICENSE for more details.
    :copyright: Copyright (c) 2018 Feei. All rights reserved
"""


class CobraException(Exception):
    """Base class for all Cobra exceptions."""


class PickupException(CobraException):
    """Base class for all Pickup exceptions."""


class PickupGitException(PickupException):
    """Base class for all Git exceptions"""


class NotExistException(PickupGitException):
    """Base class for Pickup exceptions"""


class AuthFailedException(PickupGitException):
    """Base class for Auth Failed exceptions"""
