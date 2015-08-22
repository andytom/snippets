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

from make_searchable import make_searchable

from models import db, Snippet
from forms import Confirm_Form, Search_Form, Snippit_Form


#-----------------------------------------------------------------------------#
# Config
#-----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',
                                      'config.DevelopmentConfig'))

db.init_app(app)

es = FlaskElasticsearch(app)

Misaka(app, autolink=True, escape=True, fenced_code=True, no_html=True,
       no_intra_emphasis=True, strikethrough=True, superscript=True,
       safelink=True)

Migrate(app, db)

# Update ElasicSearch after the database has been updated.
make_searchable(es, Snippet)


#-----------------------------------------------------------------------------#
# Hooks
#-----------------------------------------------------------------------------#
@app.before_request
def before_request():
    """Pre request hook"""
    g.search_form = Search_Form()


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


@app.route('/new', methods=['GET', 'POST'])
def new_snippet():
    """Page for creating new snippets.

       :returns: Returns a page to create a form. If the form is valid when it
                 is submitted create a new Snippet and redirect the user to the
                 page of the new Snippet. If the form is not valid then return
                 it is returned to the user for correction.
    """
    form = Snippit_Form()

    if form.validate_on_submit():
        new_snippet = Snippet(form.title.data, form.text.data)
        db.session.add(new_snippet)
        db.session.commit()
        flash("Created Snippet '{}'".format(new_snippet.title),
              'alert-success')
        return redirect(url_for('get_snippet', id=new_snippet.id))

    return render_template('edit_snippet.html', form=form)


#-----------------------------------------------------------------------------#
# Views - Search
#-----------------------------------------------------------------------------#
@app.route('/search', methods=['POST'])
def search():
    """Submission Endpoint for the Universal search form.

       :returns: If the search_form is valid will redirect to the results page
                 else with redirect to the page where they came from.
    """
    if g.search_form.validate_on_submit():
        return redirect(url_for('results', q=g.search_form.query.data))
    return redirect(request.referrer)


@app.route('/snippet')
def results():
    """Results page for searches.

       :results: If there is a query searches ElasticSearch and returns the
                 results. If there is no query returns the 10 most recently
                 created Snippets.
    """
    query = request.args.get('q')

    if query:
        # Set the form search field to match the query so that the form is
        # completed on the results page.
        g.search_form.query.data = query

        # Construct the query to be passed to ElasticSearch.
        body = {
            "query": {
                "query_string": {
                    "query": query,
                }
            }
        }

        results = Snippet.es_search(body=body)
        return render_template('results.html', results=results, query=query)
    else:
        results = Snippet.query.order_by(-Snippet.id).limit(10).all()
        return render_template('index.html', results=results)


#-----------------------------------------------------------------------------#
# Views - Individual Snippets
#-----------------------------------------------------------------------------#
@app.route('/snippet/<int:id>')
def get_snippet(id):
    """Returns the page for an individual Snippet.

       :param id: The id of a Snippet.

       :resutls: If the id is valid returns the page for the Snippet.
    """
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippet.html', snippet=snippet)


@app.route('/snippet/<int:id>/delete', methods=['GET', 'POST'])
def delete_snippet(id):
    """Page for deleting Snippets.

       :param id: The id of a Snippet.

       :resutls: Returns the confirmations form. If the form is submitted the
                 Snippet with the id is deleted and redirects them to the
                 index.
    """
    snippet = Snippet.query.get_or_404(id)
    form = Confirm_Form()
    question = "Are you sure you want to delete Snippet '{}'?"

    if form.validate_on_submit():
        db.session.delete(snippet)
        db.session.commit()
        flash("Snippet '{}' deleted".format(snippet.title), 'alert-success')
        return redirect(url_for('index'))

    return render_template('confirm.html',
                           form=form,
                           destructive=True,
                           question=question.format(snippet.title))


@app.route('/snippet/<int:id>/edit', methods=['GET', 'POST'])
def edit_snippet(id):
    """Page for editing Snippets.

       :param id: The id of a Snippet.

       :resutls: Returns the form for editing Snippets. If the form is valid
                 when it is submitted the Snippets is updated and the user is
                 redirected to the page for the Snippet. If the form is not
                 valid it is returned to the user for correction.
    """
    snippet = Snippet.query.get_or_404(id)
    form = Snippit_Form()

    if form.validate_on_submit():
        snippet.title, snippet.text = form.title.data, form.text.data
        db.session.add(snippet)
        db.session.commit()
        flash("Snippet '{}' Updated".format(snippet.title),
              'alert-success')
        return redirect(url_for('get_snippet', id=snippet.id))

    form.title.data = snippet.title
    form.text.data = snippet.text
    return render_template('edit_snippet.html', form=form, snippet=snippet)
