import unittest
from base import BaseTestCase


class ValidationTestCase(BaseTestCase):
    def test_create_snippet_no_title(self):
        data = {'text': 'Test Text'}

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_no_text(self):
        data = {'title': 'Test Title'}

        rv = self.app.post('/new', data=data)
        self.assertIn('This field is required.', rv.data)

    def test_create_snippet_blank(self):
        rv = self.app.post('/new', data={})

        count = rv.data.count('This field is required.')
        self.assertEqual(count, 2)
