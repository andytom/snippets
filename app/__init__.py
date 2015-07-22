from __future__ import unicode_literals
import os
from flask import Flask, request, render_template, redirect, url_for, g, flash
from flask.ext.elasticsearch import FlaskElasticsearch
from flask.ext.migrate import Migrate
from flask.ext.misaka import Misaka
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf import Form
from sqlalchemy import event
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired


#-----------------------------------------------------------------------------#
# Config
#-----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',
                                      'config.DevelopmentConfig'))

db = SQLAlchemy(app)
es = FlaskElasticsearch(app)

Misaka(app, autolink=True, escape=True, fenced_code=True, no_html=True,
       no_intra_emphasis=True, strikethrough=True, superscript=True,
       safelink=True)

Migrate(app, db)


#-----------------------------------------------------------------------------#
# Helpers
#-----------------------------------------------------------------------------#
def make_searchable(es_client, model):
    """make_searchable

       Take a SQLAlchemy database model and add hook to make sure it is
       add, updated and remove for the Elastic Search Models.

       :param es_client: A elasicsearch-py Elasticsearch object to use for the
                         interactions with ElasticSearch.
       :param model: The SQLAlchemy database model to make searchable.
    """
    def index_item(mapper, connection, target):

        data = {}
        for field in target.__es_fields__:
            data[field] = getattr(target, field)

        es_client.index(index=target.__es_index__,
                        doc_type=target.__es_doc_type__,
                        body=data,
                        id=target.id)

    def delete_item(mapper, connection, target):
        es_client.delete(index=target.__es_index__,
                         doc_type=target.__es_doc_type__,
                         id=target.id)

    event.listen(model, 'after_insert', index_item)
    event.listen(model, 'after_update', index_item)
    event.listen(model, 'after_delete', delete_item)


#-----------------------------------------------------------------------------#
# Model
#-----------------------------------------------------------------------------#
class Snippet(db.Model):
    """Snippet

       Class for our snippets that want to store and search over.
    """
    __tablename__ = 'snippet'
    __es_index__ = 'snippets'
    __es_doc_type__ = 'snippet'
    __es_fields__ = ['title', 'text']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.Text())

    def __init__(self, title, text):
        """Snippet.__init__

           :param title: The title of the Snippet
           :param text: The markdown text of the Snippet
        """
        self.title = title
        self.text = text

    def __repr__(self):
        """Snippet.__repr__

           :returns: The Unicode representation of the Snippet.
        """
        return 'Snippet({0} - {1})'.format(self.id, self.title)

    # TODO - Work out a better way to search for results
    @classmethod
    def es_search(self, q):
        """Snippet.es_search

           :param q: The query in Lucene Query Language to search ElasticSearch

           :returns: A list containing the results of the search. Each result
                     is a dict containing the id, title and text of the Snippet
        """
        es_results = es.search(index=self.__es_index__,
                               doc_type=self.__es_doc_type__,
                               q=q)
        results = []
        for hit in es_results.get('hits', {}).get('hits', []):
            res = {'id': hit.get('_id')}
            res.update(hit.get('_source'))
            results.append(res)
        return results


# Update ElasicSearch after the database has been updated.
make_searchable(es, Snippet)


#-----------------------------------------------------------------------------#
# Forms
#-----------------------------------------------------------------------------#
class Snippit_Form(Form):
    """Snippit_Form

       A Form for creating or editing Snippets
    """
    title = StringField('title', validators=[DataRequired()])
    text = TextAreaField('text', validators=[DataRequired()])


class Search_Form(Form):
    """Search_Form

       A Form for Search Queries
    """
    query = StringField('query', validators=[DataRequired()])


class Confirm_Form(Form):
    """Confirm_Form

       A Form for simple yes/no questions
    """
    pass


#-----------------------------------------------------------------------------#
# Hooks
#-----------------------------------------------------------------------------#
@app.before_request
def before_request():
    """before_request

       Pre request hook
    """
    g.search_form = Search_Form()


#-----------------------------------------------------------------------------#
# Views - Errors
#-----------------------------------------------------------------------------#
@app.errorhandler(404)
def page_not_found(error):
    """page_not_found

       Generic 404 error page.

       :param error: An exception from the error.
       :returns: The rendered 404 error template.
    """
    return render_template('page_not_found.html'), 404


#-----------------------------------------------------------------------------#
# Views - General Pages
#-----------------------------------------------------------------------------#
@app.route('/')
def index():
    """index

       Index page for the all users.

       :returns: The rendered index template.
    """
    results = Snippet.query.order_by(-Snippet.id).limit(10).all()
    return render_template('index.html', results=results)


@app.route('/new', methods=['GET', 'POST'])
def new_snippet():
    """new_snippet

       Page for creating new snippets.

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
    """search

       Submission Endpoint for the Universal search form.

       :returns: If the search_form is valid will redirect to the results page
                 else with redirect to the page where they came from.
    """
    if g.search_form.validate_on_submit():
        return redirect(url_for('results', q=g.search_form.query.data))
    return redirect(request.referrer)


@app.route('/snippet')
def results():
    """results

       Results page for searches.

       :results: If there is a query searches ElasticSearch and returns the
                 results. If there is no query returns the 10 most recently
                 created Snippets.
    """
    query = request.args.get('q')

    if query:
        g.search_form.query.data = query
        results = Snippet.es_search(q=query)
        return render_template('results.html', results=results, query=query)
    else:
        results = Snippet.query.order_by(-Snippet.id).limit(10).all()
        return render_template('index.html', results=results)


#-----------------------------------------------------------------------------#
# Views - Individual Snippets
#-----------------------------------------------------------------------------#
@app.route('/snippet/<int:id>')
def get_snippet(id):
    """get_snippet

       Returns the page for an individual Snippet.

       :param id: The id of a Snippet.

       :resutls: If the id is valid returns the page for the Snippet.
    """
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippet.html', snippet=snippet)


@app.route('/snippet/<int:id>/delete', methods=['GET', 'POST'])
def delete_snippet(id):
    """delete_snippet

       Page for deleting Snippets.

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
    """edit_snippet

       Page for editing Snippets.

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
