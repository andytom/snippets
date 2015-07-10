import os


PARENT_DIR = os.path.dirname(os.path.abspath(__file__))
TMP_DIR = os.path.join(PARENT_DIR, 'tmp')


class BaseConfig(object):
    DEBUG = True
    # For more info see the flask documentation on sessions
    # http://flask.pocoo.org/docs/0.10/quickstart/#sessions
    # You can generate a secure key using the following code
    # >>> import os
    # >>> os.urandom(24)
    SECRET_KEY = 'DEFAULT'


class TestConfig(BaseConfig):
    TESTING = True
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = 'sqlite:///:memory:'


class DevelopmentConfig(BaseConfig):
    _db = os.path.join(TMP_DIR, 'snippets.db')
    SQLALCHEMY_DATABASE_URI = 'sqlite:///{}'.format(_db)


class ProductionConfig(BaseConfig):
    DEBUG = False
    SECRET_KEY = os.environ.get('SECRET_KEY')
    SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')
