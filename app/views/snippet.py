# -*- coding: utf-8 -*-
"""
    Snippets
    ~~~~~~~~
    Snippets is a small note taking modlication.

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from flask import Blueprint, request, render_template, redirect, url_for,\
    flash, g

from app.models import db, Snippet
from app.forms import Confirm_Form, Snippit_Form


mod = Blueprint('snippet', __name__, url_prefix='/snippet')


#-- Views - General Pages ----------------------------------------------------#
@mod.route('/')
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


@mod.route('/new', methods=['GET', 'POST'])
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
        return redirect(url_for('.get_snippet', id=new_snippet.id))

    return render_template('edit_snippet.html', form=form)


#-- Individual Snippet -------------------------------------------------------#
@mod.route('/<int:id>')
def get_snippet(id):
    """Returns the page for an individual Snippet.

       :param id: The id of a Snippet.

       :resutls: If the id is valid returns the page for the Snippet.
    """
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippet.html', snippet=snippet)


@mod.route('/<int:id>/delete', methods=['GET', 'POST'])
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
                           question=question.format(snippet.title))


@mod.route('/<int:id>/edit', methods=['GET', 'POST'])
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
        return redirect(url_for('.get_snippet', id=snippet.id))

    form.title.data = snippet.title
    form.text.data = snippet.text
    return render_template('edit_snippet.html', form=form, snippet=snippet)
