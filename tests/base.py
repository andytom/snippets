# -*- coding: utf-8 -*-
"""
    Base
    ~~~~~
    Base Test case for use with all unittests

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import unittest
from app import app, db


class BaseTestCase(unittest.TestCase):
    """BaseTestCase

       Base test case for use with all unit tests contains common functions
    """
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app = app.test_client()
        self.db = db
        self.db.create_all()

    def tearDown(self):
        self.db.session.remove()
        self.db.drop_all()

    def _make_item(self, item_class, **item_kwargs):
        """Function for generating items

           :param item_class: The class of the items to create
           :param **item_kwargs: The params used to create the item these are
                                 passed to the item as kwargs

           :returns: A new item that has been added to the database
        """
        item = item_class(**item_kwargs)
        self.db.session.add(item)
        self.db.session.commit()
        return item

    def login(self, username, password):
        """Function for doing login

           :param username: The username of the user to login
           :param username: The password of the user to login

           :returns: A logged in app session
        """
        data = {
            'username': 'name',
            'password': 'password'
        }
        return self.app.post('/login', data=data, follow_redirects=True)

    def logout(self):
        """Function for doing logout

           :returns: A logged out app session
        """
        return self.app.get('/logout', follow_redirects=True)
