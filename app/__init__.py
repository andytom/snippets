# -*- coding: utf-8 -*-
"""
    Snippets
    ~~~~~~~~
    Snippets is a small note taking application.

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import os
from flask import Flask, request, render_template, redirect, url_for, g, flash
from flask.ext.elasticsearch import FlaskElasticsearch
from flask.ext.migrate import Migrate
from flask.ext.misaka import Misaka

from forms import Search_Form
from make_searchable import make_searchable
from models import db, Snippet
from views import snippet


#-----------------------------------------------------------------------------#
# Config
#-----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',
                                      'config.DevelopmentConfig'))


# Data stores related stuff
db.init_app(app)
es = FlaskElasticsearch(app)
Migrate(app, db)
make_searchable(es, Snippet)


# Front end stuff
Misaka(app, autolink=True, escape=True, fenced_code=True, no_html=True,
       no_intra_emphasis=True, strikethrough=True, superscript=True,
       safelink=True)


#-----------------------------------------------------------------------------#
# Hooks
#-----------------------------------------------------------------------------#
@app.before_request
def before_request():
    """Pre request hook"""
    g.search_form = Search_Form()


#-----------------------------------------------------------------------------#
# Blueprints
#-----------------------------------------------------------------------------#
app.register_blueprint(snippet.mod)


#-----------------------------------------------------------------------------#
# Views - Errors
#-----------------------------------------------------------------------------#
@app.errorhandler(404)
def page_not_found(error):
    """Generic 404 error page.

       :param error: An exception from the error.
       :returns: The rendered 404 error template.
    """
    return render_template('page_not_found.html'), 404


#-----------------------------------------------------------------------------#
# Views - General Pages
#-----------------------------------------------------------------------------#
@app.route('/')
def index():
    """Index page for the all users.

       :returns: The rendered index template.
    """
    results = Snippet.query.order_by(-Snippet.id).limit(10).all()
    return render_template('index.html', results=results)


@app.route('/search', methods=['POST'])
def search():
    """Submission Endpoint for the Universal search form.

       :returns: If the search_form is valid will redirect to the results page
                 else with redirect to the page where they came from.
    """
    if g.search_form.validate_on_submit():
        return redirect(url_for('snippet.results', q=g.search_form.query.data))
    return redirect(request.referrer)
