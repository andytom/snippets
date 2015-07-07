import unittest
from base import BaseTestCase


class SimpleTestCase(BaseTestCase):
    def test_create_a_snippet(self):
        rv = self.app.get('/new')
        self.assertEqual(rv.status_code, 200)

    def test_list_snippets_no_query(self):
        rv = self.app.get('/snippet')
        self.assertEqual(rv.status_code, 200)

    @unittest.skip("Need to Mock out ES")
    def test_list_snippets_with_query(self):
        rv = self.app.get('/snippet?q=test')
        self.assertEqual(rv.status_code, 200)

    def test_405_on_get_search(self):
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)
