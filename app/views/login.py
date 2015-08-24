# -*- coding: utf-8 -*-
"""
    Views Login
    ~~~~~~~~~~~
    Views for Login

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from flask import Blueprint, render_template, url_for, redirect, flash
from flask.ext.login import login_required, logout_user, login_user

from app.forms import Login_Form
from app.models import db, User


mod = Blueprint('login', __name__)


@mod.route('/login', methods=['GET', 'POST'])
def login():
    form = Login_Form()

    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        if user and user.check_password(form.password.data):
            login_user(user)
            flash('Welcome back {}!'.format(user.username), 'alert-success')
            return form.redirect('index')
        else:
            flash('Invalid Username or Password', 'alert-danger')
    return render_template('login.html', form=form)


@mod.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have been logged out', 'alert-success')
    return redirect(url_for('index'))
