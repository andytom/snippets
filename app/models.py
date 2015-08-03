from __future__ import unicode_literals
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


#-----------------------------------------------------------------------------#
# Models
#-----------------------------------------------------------------------------#
class Snippet(db.Model):
    """Class for our snippets that want to store and search over."""
    __tablename__ = 'snippet'
    __es_index__ = 'snippets'
    __es_doc_type__ = 'snippet'
    __es_fields__ = ['title', 'text']

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(64))
    text = db.Column(db.Text())

    def __init__(self, title, text):
        """Create a new Snippet

           :param title: The title of the Snippet
           :param text: The markdown text of the Snippet
        """
        self.title = title
        self.text = text

    def __repr__(self):
        """Unicode representation of the snippet.

           :returns: The Unicode representation of the Snippet.
        """
        return u'Snippet({0} - {1})'.format(self.id, self.title)
