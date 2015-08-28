# -*- coding: utf-8 -*-
"""
    Views Users
    ~~~~~~~~~~~
    Views for Users

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from flask import Blueprint, render_template, url_for, redirect
from app.models import db, User
from app.forms import User_Form


mod = Blueprint('user', __name__, url_prefix='/user')


@mod.route('/new', methods=['GET', 'POST'])
def new_user():
    form = User_Form()

    if form.validate_on_submit():
        user = User(form.username.data, form.password.data)
        db.session.add(user)
        db.session.commit()
        return redirect(url_for('.get_user', user_id=user.id))
    return render_template('add_user.html', form=form)


@mod.route('/<int:user_id>')
def get_user(user_id):
    """Page for a User

       :param user_id: ID of the User

       :returns: If the ID is for a valid user returns the page for the user.
       """
    user = User.query.get_or_404(user_id)
    return render_template('user.html', user=user)
