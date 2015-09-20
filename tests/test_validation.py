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
from app.models import User


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


class LoginValidationTestCase(BaseTestCase):
    "Test Case for checking Login Form Validation Works"

    def _get_login_dict(self):
        """Returns a dict containing all the data to log a user in

           :returns: A dict containing all the data to log a user in
        """
        login = {
            'password': 'test_password',
            'username': 'test_user',
        }
        return login

    def test_no_username(self):
        "Test that username is required"
        data = self._get_login_dict()
        data.pop('username')

        rv = self.app.post('/login', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertNotIn(data['password'], rv.data)

    def test_no_password(self):
        "Test that password is required"
        data = self._get_login_dict()
        data.pop('password')

        rv = self.app.post('/login', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertIn(data['username'], rv.data)


class UserValidateTestCase(BaseTestCase):
    "Test case for checking User Form Validation Works"

    def _get_user_dict(self):
        """Returns a dict containing all the data to build a valid user

           :returns: A dict containing all the data to build a user
        """
        user = {
            'password': 'test_password',
            'confirm': 'test_password',
            'username': 'test_user',
        }
        return user

    def test_no_password(self):
        "Test that password is required"
        data = self._get_user_dict()
        data.pop('password')

        rv = self.app.post('/user/new', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertIn(data['username'], rv.data)

    def test_no_username(self):
        "Test that username is required"
        data = self._get_user_dict()
        data.pop('username')

        rv = self.app.post('/user/new', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertNotIn(data['password'], rv.data)

    def test_duplicate_username(self):
        "Test that username is unique"
        data = self._get_user_dict()
        user = self._make_item(User, username=data['username'],
                               password=data['password'])

        rv = self.app.post('/user/new', data=data)
        self.assertIn('That username is taken.', rv.data)
        self.assertNotIn(data['password'], rv.data)

    def test_duplicate_username_case_insensetive(self):
        "Test that username is unique (case insensitive)"
        data = self._get_user_dict()
        user = self._make_item(User, username=data['username'].lower(),
                               password=data['password'])

        data['username'] = data['username'].upper()
        rv = self.app.post('/user/new', data=data)
        self.assertIn('That username is taken.', rv.data)
        self.assertNotIn(data['password'], rv.data)

    def test_no_confirm(self):
        "Test that confirm is required"
        data = self._get_user_dict()
        data.pop('confirm')

        rv = self.app.post('/user/new', data=data)
        self.assertIn('This field is required.', rv.data)
        self.assertNotIn(data['password'], rv.data)
        self.assertIn(data['username'], rv.data)

    def test_different_confirm(self):
        "Test that confirm is required"
        data = self._get_user_dict()
        data['confirm'] = 'changed'

        rv = self.app.post('/user/new', data=data)
        self.assertIn('Passwords must match', rv.data)
        self.assertNotIn(data['password'], rv.data)
        self.assertIn(data['username'], rv.data)
