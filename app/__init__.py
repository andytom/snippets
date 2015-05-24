import os
from flask import Flask, request, render_template, redirect, url_for, g, flash
from flask.ext.misaka import Misaka
from flask.ext.sqlalchemy import SQLAlchemy
from flask_wtf import Form
from wtforms import StringField, TextAreaField
from wtforms.validators import DataRequired
import flask.ext.whooshalchemy


#-----------------------------------------------------------------------------#
# Config
#-----------------------------------------------------------------------------#
app = Flask(__name__)
app.config.from_object(os.environ.get('APP_SETTINGS',
                                      'config.DevelopmentConfig'))

db = SQLAlchemy(app)

Misaka(app, fenced_code=True, intra_emphasis=False, strikethrough=True,
       superscript=True, escape=True)


#-----------------------------------------------------------------------------#
# Model
#-----------------------------------------------------------------------------#
class Snippet(db.Model):
    __tablename__ = 'snippet'
    __searchable__ = ['title', 'text']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.Text())

    def __init__(self, title, text):
        self.title = title
        self.text = text

    def __repr__(self):
        return 'Snippet({0} - {1})'.format(self.title, self.text)


# Make the model searchable
flask.ext.whooshalchemy.whoosh_index(app, Snippet)


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


@app.route('/snippet/')
@app.route('/')
def index():
    results = Snippet.query
    query = request.args.get('q')
    if query:
        g.search_form.query.data = query
        results = results.whoosh_search(query)
    else:
        results = results.order_by(-Snippet.id).limit(5)
    results = results.all()
    return render_template('results.html', results=results, query=query)


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
    form = g.search_form
    if form.validate_on_submit():
        return redirect(url_for('index', q=form.query.data))
    return redirect(url_for('index'))


@app.route('/snippet/<int:id>')
def get_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    return render_template('snippet.html', snippet=snippet)


@app.route('/snippet/<id>/delete', methods=['GET', 'POST'])
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


@app.route('/snippet/<id>/edit', methods=['GET', 'POST'])
def edit_snippet(id):
    snippet = Snippet.query.get_or_404(id)
    form = Snippit_Form()
    if form.validate_on_submit():
        snippet.title = form.title.data
        snippet.text = form.text.data
        db.session.add(snippet)
        db.session.commit()
        flash("Snippet '{}' Updated".format(snippet.title),
              'alert-success')
        return redirect(url_for('get_snippet', id=snippet.id))
    form.title.data = snippet.title
    form.text.data = snippet.text
    return render_template('edit_snippet.html', form=form, snippet=snippet)
