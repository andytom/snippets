from base import BaseTestCase


class SimpleTestCase(BaseTestCase):
    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)

    def test_create_a_snippet(self):
        rv = self.app.get('/new')
        self.assertEqual(rv.status_code, 200)

    def test_list_snippets_no_query(self):
        rv = self.app.get('/snippet')
        # Should redirect to '/'
        self.assertEqual(rv.status_code, 301)

    def test_404_on_missing(self):
        rv = self.app.get('/snippet/fake')
        self.assertEqual(rv.status_code, 404)

    def test_405_on_get_search(self):
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)
