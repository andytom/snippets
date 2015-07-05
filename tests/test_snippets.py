import unittest
from app import Snippet
from base import BaseTestCase


class NoSnippetsTestCase(BaseTestCase):
    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)

    def test_404_on_get_snippet(self):
        rv = self.app.get('/snippet/1')
        self.assertEqual(rv.status_code, 404)

    @unittest.skip("Need to Mock out ES")
    def test_search(self):
        rv = self.app.get('/snippet/?q=test')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)


class SnippetTestCase(BaseTestCase):
    @unittest.skip("Need to Mock out ES")
    def test_create_snippet(self):
        data = {'title': 'Test Title',
                'text': 'Test Text'}
        rv = self.app.post('/new', data=data)

        snippet = Snippet.query.all()[0]
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    @unittest.skip("Need to Mock out ES")
    def test_snippet_update(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        data = {'title': 'Test Title Update',
                'text': 'Test Text Update'}
        rv = self.app.post('/snippet/{}/edit'.format(snippet.id), data=data)

        snippet = Snippet.query.get(snippet.id)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    @unittest.skip("Need to Mock out ES")
    def test_snippet_delete(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        rv = self.app.post('/snippet/{}/delete'.format(snippet.id))

        self.assertEqual(None, Snippet.query.get(snippet.id))

    @unittest.skip("Need to Mock out ES")
    def test_search(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        rv = self.app.get('/snippet/?q=Test')

        self.assertEqual(rv.status_code, 200)
        self.assertEqual(snippet.title, rv.data)
        self.assertEqual(snippet.text, rv.data)
        self.assertFalse('No results for query' in rv.data)
