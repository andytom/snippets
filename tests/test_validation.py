# -*- coding: utf-8 -*-
"""
    Validation
    ~~~~~~~~~~
    All test cases relating to form validation

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import unittest
from base import BaseTestCase


class SnippetValidationTestCase(BaseTestCase):
    "Test Case for checking that Snippet Form Validation Works."

    def _get_snippet_dict(self):
        """Returns a dict containing all the data to build a valid snippet

           :returns: A dict containing all the data to build a Snippet
        """
        snippet = {
            'text': 'Test Text',
            'title': 'Test Title',
        }
        return snippet

    def test_create_snippet_no_title(self):
        "Test for snippet with no title."
        data = self._get_snippet_dict()
        data.pop('title')

        rv = self.app.post('/snippet/new', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertIn(data['text'], rv.data)

    def test_create_snippet_no_text(self):
        "Test for snippet with no text."
        data = self._get_snippet_dict()
        data.pop('text')

        rv = self.app.post('/snippet/new', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertIn(data['title'], rv.data)


class UserValidationTestCase(BaseTestCase):
    "Test Case for checking Login Form Validation Works"

    def _get_user_dict(self):
        """Returns a dict containing all the data to build a valid user

           :returns: A dict containing all the data to build a user
        """
        user = {
            'password': 'test_password',
            'username': 'test_user',
        }
        return user

    def test_no_username(self):
        "Test that username is required"
        data = self._get_user_dict()
        data.pop('username')

        rv = self.app.post('/login', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertNotIn(data['password'], rv.data)

    def test_no_password(self):
        "Test that password is required"
        data = self._get_user_dict()
        data.pop('password')

        rv = self.app.post('/login', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertIn(data['username'], rv.data)
