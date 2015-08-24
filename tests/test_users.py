# -*- coding: utf-8 -*-
"""
    Test User
    ~~~~~~~~~
    All test cases relating to Users

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import unittest
from sqlalchemy.exc import IntegrityError
from app.models import User
from base import BaseTestCase


class UsersModelTestCase(BaseTestCase):
    "Tests for User Models"

    def test_user_hash_password(self):
        "Test that the password is hashed when the user is created"
        user = self._make_item(User, username='name', password='password')
        self.assertFalse(user.hashed_password == 'password')
        self.assertTrue(user.check_password('password'))
        self.assertFalse(user.check_password('incorrect'))

    def test_user_change_password(self):
        "Test that the password is updated correctly"
        user = self._make_item(User, username='name', password='password')
        user.set_password('updated')
        self.assertFalse(user.check_password('password'))
        self.assertTrue(user.check_password('updated'))

    def test_user_unique_username(self):
        "Test that creating a user with a duplicate username fails"
        user_kwargs = {
            'item_class': User,
            'username': 'name',
            'password': 'password'
        }
        user = self._make_item(**user_kwargs)
        self.assertRaises(IntegrityError, self._make_item, **user_kwargs)


class NoUserTestCase(BaseTestCase):
    "Tests for Logging a user in"

    def test_login_user(self):
        "Test that logins work"
        user = self._make_item(User, username='name', password='password')

        rv = self.login('name', 'password')
        self.assertIn('Welcome back {}!'.format(user.username), rv.data)

    def test_login_case_insensitive_user(self):
        "Test that logins are case insensitive"
        user = self._make_item(User, username='name', password='password')

        rv = self.login('NAME', 'password')
        self.assertIn('Welcome back {}!'.format(user.username), rv.data)

    def test_logout_user(self):
        "Test that logout work"
        user = self._make_item(User, username='name', password='password')

        rv = self.login('name', 'password')
        rv = self.logout()
        self.assertIn('You have been logged out', rv.data)
