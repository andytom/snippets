from __future__ import unicode_literals
import unittest
from base import BaseTestCase


class ValidationTestCase(BaseTestCase):
    """ValidationTestCase

       Test Case for checking that Form Validation Works.
    """
    def test_create_snippet_no_title(self):
        """test_create_snippet_no_title

           Test for snippet with no title.
        """
        data = {'text': 'Test Text'}

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_no_text(self):
        """test_create_snippet_no_text

           Test for snippet with no text.
        """
        data = {'title': 'Test Title'}

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_blank(self):
        """test_create_snippet_blank

           Test for submission of empty form.
        """
        rv = self.app.post('/new', data={})

        count = rv.data.count('This field is required.')
        self.assertEqual(count, 2)
