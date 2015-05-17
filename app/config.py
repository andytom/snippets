import os

DEBUG = False

# For more info see the flask documentation on sessions
# http://flask.pocoo.org/docs/0.10/quickstart/#sessions
# You can generate a secure key using the following code
# >>> import os
# >>> os.urandom(24)
SECRET_KEY = os.environ.get('SECRET_KEY')

# Connection details for the Database
# See the Flask-SQLAlchemy docs
# https://pythonhosted.org/Flask-SQLAlchemy/config.html#connection-uri-format
SQLALCHEMY_DATABASE_URI = os.environ.get('DATABASE_URL')

# Full path to where should the Whoosh indexes be stored
parent_dir = os.path.dirname(os.path.abspath(__file__))
WHOOSH_BASE = os.path.join(parent_dir, 'snippet_index')
