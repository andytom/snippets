# -*- coding: utf-8 -*-
"""
    Models
    ~~~~~~
    SQLAlchemy Models for Snippets

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import bcrypt
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.login import UserMixin


#-----------------------------------------------------------------------------#
# Setup
#-----------------------------------------------------------------------------#
db = SQLAlchemy()


#-----------------------------------------------------------------------------#
# Models
#-----------------------------------------------------------------------------#
class Snippet(db.Model):
    """Class for our snippets that want to store and search over."""
    __tablename__ = 'snippet'
    __es_index__ = 'snippets'
    __es_doc_type__ = 'snippet'
    __es_fields__ = ['title', 'text']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.Text())

    def __init__(self, title, text):
        """Create a new Snippet

           :param title: The title of the Snippet
           :param text: The markdown text of the Snippet
        """
        self.title = title
        self.text = text

    def __repr__(self):
        """Unicode representation of the snippet.

           :returns: The Unicode representation of the Snippet.
        """
        return u'Snippet({0} - {1})'.format(self.id, self.title)


class User(db.Model, UserMixin):
    """Class to represent Users"""
    __tablename__ = 'user'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(64, collation='NOCASE'), unique=True)
    hashed_password = db.Column(db.String(60))

    def __init__(self, username, password):
        """Create a new User

           :param username: The username of the User
           :param password: The password of the User (this will be hashed)
        """
        self.username = username
        self.set_password(password)

    def __repr__(self):
        """Unicode representation of the user.

           :returns: The Unicode representation of the User.
        """
        return u'User({0} - {1})'.format(self.id, self.username)

    def set_password(self, password):
        """Hash the password and store it

           :param password: The password to hash and store.
        """
        self.hashed_password = bcrypt.hashpw(password.encode('utf-8'),
                                             bcrypt.gensalt())

    def check_password(self, password):
        """Check the passed password against the stored hash

           :param password: The password to check.

           :returns: True if the password matched the current stored hash
                     and False otherwise
        """
        test = bcrypt.hashpw(password.encode('utf-8'),
                             self.hashed_password.encode('utf-8'))

        return test == self.hashed_password
