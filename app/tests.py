from __future__ import unicode_literals
import unittest
from app import app, db


class BaseTestCase(unittest.TestCase):
    def setUp(self):
        app.config['TESTING'] = True
        app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite://'
        app.config['WTF_CSRF_ENABLED'] = False
        self.app = app.test_client()
        db.create_all()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_create_a_snippet(self):
        rv = self.app.get('/new')
        self.assertEqual(rv.status_code, 200)

    def test_list_snippets(self):
        rv = self.app.get('/snippet')
        # Should redirect to '/'
        self.assertEqual(rv.status_code, 301)

    def test_404_on_missing(self):
        rv = self.app.get('/snippet/fake')
        self.assertEqual(rv.status_code, 404)

    def test_405_on_get_search(self):
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)

if __name__ == '__main__':
    unittest.main()
