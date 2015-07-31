from __future__ import unicode_literals
from flask.ext.sqlalchemy import SQLAlchemy


db = SQLAlchemy()


#-----------------------------------------------------------------------------#
# Models
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
    def es_search(self, es, q):
        """Snippet.es_search

           :param es: The ElasticSearch client that we want to use for
                      searching.
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
