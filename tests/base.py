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
        """Function for generating users

           :param item_class: The class of the items to create
           :param **item_kwargs: The params used to create the item these are
                                 passed to the item as kwargs

           :returns: A new item that has been added to the database
        """
        item = item_class(**item_kwargs)
        self.db.session.add(item)
        self.db.session.commit()
        return item
