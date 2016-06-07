#-*- coding: utf-8 -*-

from __future__ import absolute_import, division, print_function, unicode_literals

import os

undefined = object()


def rel(*path):
    """
    Converts path relative to the project root into an absolute path

    :rtype: str
    """
    return os.path.abspath(
        os.path.join(
            os.path.dirname(__file__),
            os.path.pardir,
            *path
        )
    ).replace("\\", "/")


def get_env_setting(setting, default=undefined):
    """
    Get the environment setting or raise exception

    :rtype: str
    """

    try:
        return os.environ[setting]
    except KeyError:
        if default is not undefined:
            return default
        error_msg = "Set the %s env variable" % setting
        from django.core.exceptions import ImproperlyConfigured
        raise ImproperlyConfigured(error_msg)