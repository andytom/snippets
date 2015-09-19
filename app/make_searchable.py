# -*- coding: utf-8 -*-
"""
    Make Searchable
    ~~~~~~~~~~~~~~~
    Helper methods to make updating SQLAlchemy models indexed in ElasticSearch

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from functools import partial
import elasticsearch
from sqlalchemy import event


#-----------------------------------------------------------------------------#
# Helpers
#-----------------------------------------------------------------------------#
def do_index_item(es_client, item):
    """Take the passed item and add it to the index using the passed
       ElasticSearch client.

       :param es_client: A elasicsearch-py Elasticsearch object to use for the
                         interactions with ElasticSearch.
       :param item: The SQLAlchemy database object to be indexed.
    """
    data = {}
    for field in item.__es_fields__:
        data[field] = getattr(item, field)

    es_client.index(index=item.__es_index__,
                    doc_type=item.__es_doc_type__,
                    body=data,
                    id=item.id)


def do_delete_item(es_client, model, item_id):
    """Remove a document from the ElasticSearch index.

       :param es_client: A elasicsearch-py Elasticsearch object to use for the
                         interactions with ElasticSearch.
       :param item_id: The ID to be removed from the index.
       :param model: The SQLAlchemy database model of the item.
    """
    try:
        es_client.delete(index=model.__es_index__,
                         doc_type=model.__es_doc_type__,
                         id=item_id)
    except elasticsearch.exceptions.NotFoundError:
        # If it can't be found assume it has already been deleted
        pass


def es_search(cls, es_client, **search_kwargs):
    """Search in ElasticSearch for this item.

       :param es_client: The ElasticSearch client that we want to use for
                         searching.
       :param **search_kwargs: The remaining kwargs are passed to the
                               es_clinet.search function. The index is always
                               set to cls.__es_index__ and the doc_type is set
                               to cls.__es_doc_type__.

       :returns: A list of the results objects
    """
    DEFAULTS = {
        'index': cls.__es_index__,
        'doc_type': cls.__es_doc_type__,
    }

    # Overwrite with the fixed values
    search_kwargs.update(DEFAULTS)

    # Get our ordered results from ES
    es_results = es_client.search(**search_kwargs)
    hits = es_results.get('hits', {}).get('hits', [])
    ids = [hit['_id'] for hit in hits]

    # Bail out early if we got no ids back
    if not ids:
        return []

    # Fetch all the results from the database then order them to match the
    # resutls that we got from ElasticSearch
    #
    # We need to use the unicode of the item.id when searching since
    # ElasticSearch returns the id a unicode string even if it is an int.
    results = list(cls.query.filter(cls.id.in_(ids)).all())

    results.sort(key=lambda item: ids.index(unicode(item.id)))

    return results


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
def make_searchable(es_client, model):
    """Take a SQLAlchemy database model and add hook to make sure it is
       added, updated and remove for the Elastic Search Models. Also adds the
       classmehod 'es_search' for simple searching.

       Requires that the model has '__es_index__', '__es_doc_type__' and
       '__es_fields__' atributes. Where:
       * '__es_index__' is the ElasticSearch index this model should be added
         to.
       * '__es_doc_type__' is the Docuemnt type for this model.
       * '__es_fields__' is a list of fields to be included in the index.

       :param es_client: A elasicsearch-py Elasticsearch object to use for the
                         interactions with ElasticSearch.
       :param model: The SQLAlchemy database model to make searchable.
    """
    def index_item(mapper, connection, target):
        do_index_item(es_client, target)

    def delete_item(mapper, connection, target):
        do_delete_item(es_client, model, target)

    event.listen(model, 'after_insert', index_item)
    event.listen(model, 'after_update', index_item)
    event.listen(model, 'after_delete', delete_item)

    model.es_search = classmethod(partial(es_search, es_client=es_client))
