from __future__ import unicode_literals
import unittest
from base import BaseTestCase


class ValidationTestCase(BaseTestCase):
    """ValidationTestCase

       Test Case for checking that Form Validation Works.
    """

    def _get_snippet_dict(self):
        """_get_snippet_dict

           :returns: A dict containing all the args to build a Snippet
        """
        snippet = {
            'text': 'Test Text',
            'title': 'Test Title',
        }
        return snippet

    def test_create_snippet_no_title(self):
        """test_create_snippet_no_title

           Test for snippet with no title.
        """
        data = self._get_snippet_dict()
        data.pop('title')

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_no_text(self):
        """test_create_snippet_no_text

           Test for snippet with no text.
        """
        data = self._get_snippet_dict()
        data.pop('text')

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_blank(self):
        """test_create_snippet_blank

           Test for submission of empty form.
        """
        rv = self.app.post('/new', data={})

        count = rv.data.count('This field is required.')
        self.assertEqual(count, 2)
