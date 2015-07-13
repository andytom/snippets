import os
from flask import Flask, request, render_template, redirect, url_for, g, flash
from flask.ext.misaka import Misaka
from flask.ext.sqlalchemy import SQLAlchemy
from flask.ext.elasticsearch import FlaskElasticsearch
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
from sqlalchemy import event


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


#-----------------------------------------------------------------------------#
# Helpers
#-----------------------------------------------------------------------------#
def make_searchable(es_client, model):
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
    __tablename__ = 'snippet'
    __es_index__ = 'snippets'
    __es_doc_type__ = 'snippet'
    __es_fields__ = ['title', 'text']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.Text())

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return 'Snippet({0} - {1})'.format(self.id, self.title)

    # TODO - Work out a better way to search for results
    @classmethod
    def es_search(self, q):
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
    title = StringField('title', validators=[DataRequired()])
    text = TextAreaField('text', validators=[DataRequired()])


class Search_Form(Form):
    query = StringField('query', validators=[DataRequired()])


class Confirm_Form(Form):
    pass


#-----------------------------------------------------------------------------#
# Hooks
#-----------------------------------------------------------------------------#
@app.before_request
def before_request():
    g.search_form = Search_Form()


#-----------------------------------------------------------------------------#
# Views
#-----------------------------------------------------------------------------#
@app.errorhandler(404)
def page_not_found(error):
    return render_template('page_not_found.html'), 404


@app.route('/')
def index():
    results = Snippet.query.order_by(-Snippet.id).limit(10).all()
    return render_template('index.html', results=results)


@app.route('/new', methods=['GET', 'POST'])
def new_snippet():
    form = Snippit_Form()

    if form.validate_on_submit():
        new_snippet = Snippet(form.title.data, form.text.data)
        db.session.add(new_snippet)
        db.session.commit()
        flash("Created Snippet '{}'".format(new_snippet.title),
              'alert-success')
        return redirect(url_for('get_snippet', id=new_snippet.id))

    return render_template('edit_snippet.html', form=form)


@app.route('/search', methods=['POST'])
def search():
    if g.search_form.validate_on_submit():
        return redirect(url_for('results', q=g.search_form.query.data))
    return redirect(url_for('index'))


@app.route('/snippet')
def results():
    query = request.args.get('q')

    if query:
        g.search_form.query.data = query
        results = Snippet.es_search(q=query)
        return render_template('results.html', results=results, query=query)
    else:
        results = Snippet.query.order_by(-Snippet.id).limit(10).all()
        return render_template('index.html', results=results)


@app.route('/snippet/<int:id>')
def get_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippet.html', snippet=snippet)


@app.route('/snippet/<int:id>/delete', methods=['GET', 'POST'])
def delete_snippet(id):
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
