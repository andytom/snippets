from __future__ import unicode_literals
import unittest
from app import app, db


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config.from_object('config.TestConfig')
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()
