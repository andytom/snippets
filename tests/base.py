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
