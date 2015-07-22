import unittest
from app import Snippet, es
from base import BaseTestCase


def fake_index(*args, **kwargs):
    """fake_index"""
    pass


def fake_delete(*args, **kwargs):
    """fake_delete"""
    pass


def make_fake_search(results):
    """make_fake_search

       Makes a dummy ElasticSearch search function that returns the passed
       resutls

       :param resutls: A dict of resutls to be returned by the fake search
                       function.
    """
    def fake_search(*args, **kwargs):
        return results
    es.search = fake_search


es.index = fake_index
es.delete = fake_delete


class NoSnippetsTestCase(BaseTestCase):
    """NoSnippetsTestCase

       Test Case for all tests when no Snippets have been added
    """
    def test_405_on_get_search(self):
        """test_405_on_get_search

           /search is an endpoint just for submitting the search form. So is
           post only.
        """
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)

    def test_create_a_snippet(self):
        """test_create_a_snippet

           Test that we can get the page to create a new Snippet
        """
        rv = self.app.get('/new')
        self.assertEqual(rv.status_code, 200)

    def test_index(self):
        """test_index

           Test that we can get the index and there are no results
        """
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)

    def test_404_on_get_snippet(self):
        """test_404_on_get_snippet

           Test that get a 404 when there are no Snippets
        """
        rv = self.app.get('/snippet/1')
        self.assertEqual(rv.status_code, 404)

    def test_search(self):
        """test_search

           Test that we don't get an search results when the Database is
           empty.
        """
        make_fake_search({})

        rv = self.app.get('/snippet?q=test')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)

    def test_search_no_query(self):
        """test_search_no_query

           Test that we get the correct answer when there is no query.
        """
        rv = self.app.get('/snippet')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)


class SnippetTestCase(BaseTestCase):
    """SnippetTestCase

       Test Case for all tests when Snippets have been added
    """
    def _make_snippet(self, **snippet_args):
        """_make_snippet

           Function for generating snippets

           :params: All Parameters are passed to create the Snippet

           :returns: A Snippet created with the args passed to the params
        """
        snippet = Snippet(**snippet_args)
        self.db.session.add(snippet)
        self.db.session.commit()
        return snippet

    def test_create_snippet(self):
        """test_create_snippet

           Test the creation of a snippet
        """
        data = {'title': 'Test Title',
                'text': 'Test Text'}
        rv = self.app.post('/new', data=data)

        # There will only be one snippet.
        snippet = Snippet.query.all()[0]
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    def test_snippet_update(self):
        """test_snippet_update

           Test updating a snippet.
        """
        snippet = self._make_snippet(title='Test Title', text='Test Text')

        data = {'title': 'Test Title Update',
                'text': 'Test Text Update'}
        rv = self.app.post('/snippet/{}/edit'.format(snippet.id), data=data)

        snippet = Snippet.query.get(snippet.id)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    def test_snippet_delete(self):
        """test_snippet_delete

           Test deleting a snippet
        """
        snippet = self._make_snippet(title='Test Title', text='Test Text')

        rv = self.app.post('/snippet/{}/delete'.format(snippet.id))

        self.assertEqual(None, Snippet.query.get(snippet.id))

    def test_search_with_results(self):
        """test_search_with_results

           Test that a valid search returns a result and the returned result is
           processed correctly
        """
        snippet = self._make_snippet(title='Test Title', text='Test Text')

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
        """test_search_without_results

           Test that an invalid search doesn't return resutls.
        """
        snippet = self._make_snippet(title='Test Title', text='Test Text')

        make_fake_search({})

        rv = self.app.get('/snippet?q=aaaaaaaaa')

        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)
