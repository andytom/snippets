# -*- coding: utf-8 -*-
"""
    Snippets
    ~~~~~~~~
    All test cases relating to Snippets

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import json
import os
import unittest
import vcr
from app import Snippet
from base import BaseTestCase


PARENT_DIR = os.path.dirname(os.path.abspath(__file__))

my_vcr = vcr.VCR(
    cassette_library_dir=os.path.join(PARENT_DIR, 'fixtures'),
    path_transformer=vcr.VCR.ensure_suffix('.yaml')
)


class NoSnippetsTestCase(BaseTestCase):
    """Test Case for all tests when no Snippets have been added"""

    def test_405_on_get_search(self):
        """/search is an endpoint just for submitting the search form. So is
           post only.
        """
        rv = self.app.get('/search')
        self.assertEqual(rv.status_code, 405)

    @my_vcr.use_cassette()
    def test_search_redirect(self):
        """Test that we get redirected correctly when posting to search"""
        data = {'query': 'test'}
        rv = self.app.post('/search', data=data, follow_redirects=True)
        self.assertIn('No results for query', rv.data)

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

    @my_vcr.use_cassette()
    def test_search(self):
        """Test that we don't get an search results when the Database is
           empty.
        """
        rv = self.app.get('/snippet/?q=test')
        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)

    def test_search_no_query(self):
        """Test that we get the correct answer when there is no query."""
        rv = self.app.get('/snippet/')
        self.assertEqual(rv.status_code, 200)
        self.assertIn("There are no snippets.", rv.data)

    def test_preview_render(self):
        """Test that we can preview"""
        data = {'title': 'Test Title',
                'text': 'Test Text'}

        rv = self.app.post('/snippet/render', data=json.dumps(data),
                           headers=[('Content-Type', 'application/json')])
        rv_json = json.loads(rv.data)

        self.assertIn(data['title'], rv_json['html'])
        self.assertIn(data['text'], rv_json['html'])

    def test_preview_render_not_valid(self):
        """Test that we get 400s on when not JSON"""
        data = {'title': 'Test Title',
                'text': 'Test Text'}

        rv = self.app.post('/snippet/render', data=data)
        self.assertEqual(rv.status_code, 400)

    def test_preview_render_not_a_post(self):
        """Test that can't do a GET"""
        rv = self.app.get('/snippet/render')
        self.assertEqual(rv.status_code, 405)


class SnippetTestCase(BaseTestCase):
    """Test Case for all tests when Snippets have been added"""

    @my_vcr.use_cassette()
    def test_create_snippet(self):
        """Test the creation of a snippet"""
        data = {'title': 'Test Title',
                'text': 'Test Text'}
        rv = self.app.post('/snippet/new', data=data)

        # There will only be one snippet.
        snippet = Snippet.query.first()
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    @my_vcr.use_cassette()
    def test_snippet_update(self):
        """Test updating a snippet."""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        data = {'title': 'Test Title Update',
                'text': 'Test Text Update'}
        rv = self.app.post('/snippet/{}/edit'.format(snippet.id), data=data)

        snippet = Snippet.query.get(snippet.id)
        self.assertEqual(snippet.title, data['title'])
        self.assertEqual(snippet.text, data['text'])

    @my_vcr.use_cassette()
    def test_snippet_delete(self):
        """Test deleting a snippet"""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        rv = self.app.post('/snippet/{}/delete'.format(snippet.id))

        self.assertEqual(None, Snippet.query.get(snippet.id))

    @my_vcr.use_cassette()
    def test_search_with_results(self):
        """Test that a valid search returns a result and the returned result is
           processed correctly
        """
        snippet = self._make_item(Snippet, title='Title', text='Text')

        rv = self.app.get('/snippet/?q=Test')

        self.assertEqual(rv.status_code, 200)
        self.assertIn(snippet.title, rv.data)
        self.assertIn(snippet.text, rv.data)
        self.assertFalse('No results for query' in rv.data)

    @my_vcr.use_cassette()
    def test_search_without_results(self):
        """Test that an invalid search doesn't return resutls."""
        snippet = self._make_item(Snippet, title='Title', text='Text')

        rv = self.app.get('/snippet/?q=aaaaaaaaa')

        self.assertEqual(rv.status_code, 200)
        self.assertIn('No results for query', rv.data)
