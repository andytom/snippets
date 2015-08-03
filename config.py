# -*- coding: utf-8 -*-
"""
    Config
    ~~~~~~
    All the different config for each environment

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import os


PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class BaseConfig(object):
    """BaseConfig

       The base config all other config should inherit from this
    """
    DEBUG = True
    # For more info see the flask documentation on sessions
    # http://flask.pocoo.org/docs/0.10/quickstart/#sessions
    # You can generate a secure key using the following code
    # >>> import os
    # >>> os.urandom(24)
    SECRET_KEY = 'DEFAULT'


class TestConfig(BaseConfig):
    """TestConfig

       The config for use when testing the App
    """
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DevelopmentConfig(BaseConfig):
    """DevelopmentConfig

       The config for use when developing on a local machine
    """
    _db = os.path.join(TMP_DIR, 'snippets.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(_db)


class ProductionConfig(BaseConfig):
    """ProductionConfig

       The config for use in production.
    """
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
