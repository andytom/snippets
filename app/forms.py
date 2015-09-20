# -*- coding: utf-8 -*-
"""
    Forms
    ~~~~~
    Custom WTForms for Snippets

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from urlparse import urlparse, urljoin
from flask import request, url_for, redirect
from flask_wtf import Form
from wtforms import StringField, TextAreaField, HiddenField, PasswordField
from wtforms.validators import DataRequired, EqualTo, ValidationError
from models import User


#-- Redirect form ------------------------------------------------------------#
# Taken from  http://flask.pocoo.org/snippets/63/
def is_safe_url(target):
    ref_url = urlparse(request.host_url)
    test_url = urlparse(urljoin(request.host_url, target))
    return test_url.scheme in ('http', 'https') and \
        ref_url.netloc == test_url.netloc


def get_redirect_target():
    for target in request.args.get('next'), request.referrer:
        if not target:
            continue
        if is_safe_url(target):
            return target


class Redirect_Form(Form):
    next = HiddenField()

    def __init__(self, *args, **kwargs):
        Form.__init__(self, *args, **kwargs)
        if not self.next.data:
            self.next.data = get_redirect_target() or ''

    def redirect(self, endpoint='index', **values):
        if is_safe_url(self.next.data):
            return redirect(self.next.data)
        target = get_redirect_target()
        return redirect(target or url_for(endpoint, **values))


#-- Validators ---------------------------------------------------------------#
class Unique(object):
    "A Vaidator for Unique fields"
    def __init__(self, model, column, message=None):
        """Test is a there is already a record in the database that matches
           the field.

           :param model: The SQLAlchemy database model for the record
           :param column: The SQLAlchemy column to search for a match
           :param message: Message to raise if the field fails validation
        """
        self.model = model
        self.column = column
        if not message:
            message = 'Field must be unique'
        self.message = message

    def __call__(self, form, field):
        if self.model.query.filter(self.column == field.data).count():
            raise ValidationError(self.message)


#-- Forms --------------------------------------------------------------------#
class Snippit_Form(Form):
    "A Form for creating or editing Snippets"
    title = StringField('Title', validators=[DataRequired()])
    text = TextAreaField('Text', validators=[DataRequired()])


class Search_Form(Form):
    "A Form for Search Queries"
    query = StringField('Query', validators=[DataRequired()])


class Confirm_Form(Form):
    "A Form for simple yes/no questions"
    pass


class User_Form(Form):
    "A Form for creating User"
    username = StringField('Username',
                           validators=[DataRequired(),
                                       Unique(User, User.username,
                                       message='That username is taken.')])
    password = PasswordField('Password', validators=[DataRequired()])
    confirm = PasswordField('Confirm Password',
                            validators=[DataRequired(),
                                        EqualTo('password',
                                        message='Passwords must match')])


class Login_Form(Redirect_Form):
    "A Form for logining Users in"
    username = StringField('Username', validators=[DataRequired()])
    password = PasswordField('Password', validators=[DataRequired()])
