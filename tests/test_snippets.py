import unittest
from app import Snippet, es
from base import BaseTestCase


def fake_index(*args, **kwargs):
    pass


def fake_delete(*args, **kwargs):
    pass


def make_fake_search(results):
    def fake_search(*args, **kwargs):
        return results
    es.search = fake_search


es.index = fake_index
es.delete = fake_delete


class NoSnippetsTestCase(BaseTestCase):
    def test_405_on_get_search(self):
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)

    def test_create_a_snippet(self):
        rv = self.app.get('/new')
        self.assertEqual(rv.status_code, 200)

    def test_index(self):
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)

    def test_404_on_get_snippet(self):
        rv = self.app.get('/snippet/1')
        self.assertEqual(rv.status_code, 404)

    def test_search(self):
        make_fake_search({})

        rv = self.app.get('/snippet?q=test')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)

    def test_search_no_query(self):
        rv = self.app.get('/snippet')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)


class SnippetTestCase(BaseTestCase):
    def test_create_snippet(self):
        data = {'title': 'Test Title',
                'text': 'Test Text'}
        rv = self.app.post('/new', data=data)

        # There will only be one snippet.
        snippet = Snippet.query.all()[0]
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

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

    def test_snippet_delete(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        rv = self.app.post('/snippet/{}/delete'.format(snippet.id))

        self.assertEqual(None, Snippet.query.get(snippet.id))

    def test_search_with_results(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        make_fake_search({'hits': {'hits': [{'_id': snippet.id,
                                            '_source': {
                                                'title': snippet.title,
                                                'text': snippet.text,
                                                }}]}})

        rv = self.app.get('/snippet?q=Test')

        self.assertEqual(rv.status_code, 200)
        self.assertIn(snippet.title, rv.data)
        self.assertIn(snippet.text, rv.data)
        self.assertFalse('No results for query' in rv.data)

    def test_search_without_results(self):
        snippet = Snippet('Test Title', 'Test Text')
        self.db.session.add(snippet)
        self.db.session.commit()

        make_fake_search({})

        rv = self.app.get('/snippet?q=aaaaaaaaa')

        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)
