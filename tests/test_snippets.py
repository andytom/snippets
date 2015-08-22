# -*- coding: utf-8 -*-
"""
    Snippets
    ~~~~~~~~
    All test cases relating to Snippets

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import unittest
from app import Snippet, es
from base import BaseTestCase


def fake_index(*args, **kwargs):
    """NOOP index for testing"""
    pass


def fake_delete(*args, **kwargs):
    """NOOP delete for testing"""
    pass


def make_fake_search(results):
    """Makes a dummy ElasticSearch search function that returns the passed
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
    """Test Case for all tests when no Snippets have been added"""

    def test_405_on_get_search(self):
        """/search is an endpoint just for submitting the search form. So is
           post only.
        """
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)

    def test_create_a_snippet(self):
        """Test that we can get the page to create a new Snippet"""
        rv = self.app.get('/snippet/new')
        self.assertEqual(rv.status_code, 200)

    def test_index(self):
        """Test that we can get the index and there are no results"""
        rv = self.app.get('/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)

    def test_404_on_get_snippet(self):
        """Test that get a 404 when there are no Snippets"""
        rv = self.app.get('/snippet/1')
        self.assertEqual(rv.status_code, 404)

    def test_search(self):
        """Test that we don't get an search results when the Database is
           empty.
        """
        make_fake_search({})

        rv = self.app.get('/snippet/?q=test')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)

    def test_search_no_query(self):
        """Test that we get the correct answer when there is no query."""
        rv = self.app.get('/snippet/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)


class SnippetTestCase(BaseTestCase):
    """Test Case for all tests when Snippets have been added"""

    def test_create_snippet(self):
        """Test the creation of a snippet"""
        data = {'title': 'Test Title',
                'text': 'Test Text'}
        rv = self.app.post('/snippet/new', data=data)

        # There will only be one snippet.
        snippet = Snippet.query.all()[0]
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    def test_snippet_update(self):
        """Test updating a snippet."""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        data = {'title': 'Test Title Update',
                'text': 'Test Text Update'}
        rv = self.app.post('/snippet/{}/edit'.format(snippet.id), data=data)

        snippet = Snippet.query.get(snippet.id)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    def test_snippet_delete(self):
        """Test deleting a snippet"""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        rv = self.app.post('/snippet/{}/delete'.format(snippet.id))

        self.assertEqual(None, Snippet.query.get(snippet.id))

    def test_search_with_results(self):
        """Test that a valid search returns a result and the returned result is
           processed correctly
        """
        snippet = self._make_item(Snippet, title='Title', text='Text')

        make_fake_search({'hits': {'hits': [{
                                            '_id': unicode(snippet.id),
                                            '_source': {
                                                'title': snippet.title,
                                                'text': snippet.text,
                                            }
                                            }]
                                   }
                          })

        rv = self.app.get('/snippet/?q=Test')

        self.assertEqual(rv.status_code, 200)
        self.assertIn(snippet.title, rv.data)
        self.assertIn(snippet.text, rv.data)
        self.assertFalse('No results for query' in rv.data)

    def test_search_without_results(self):
        """Test that an invalid search doesn't return resutls."""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        make_fake_search({})

        rv = self.app.get('/snippet/?q=aaaaaaaaa')

        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)
