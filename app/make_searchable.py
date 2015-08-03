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


def es_search(cls, es_client, **kwargs):
    """Search over the item

       :param es_client: The ElasticSearch client that we want to use for
                         searching.
       :param kwargs: The remaining kwargs are passed to the es_clinet.search
                      function. If not set the index defaults to
                      cls.__es_index__ and the doc_type defaults to
                      cls.__es_doc_type__

       :returns: A tuple containg a list of the results of the search where
                 each result is a dict containing the id and '_source' fields
                 and the raw results from ElasticSearch.
    """
    search_kwargs = {
        'index': cls.__es_index__,
        'doc_type': cls.__es_doc_type__,
    }

    # Merge the passed in kwargs over the defaults.
    search_kwargs.update(kwargs)
    es_results = es_client.search(**search_kwargs)

    results = []
    for hit in es_results.get('hits', {}).get('hits', []):
        res = {'id': hit.get('_id')}
        res.update(hit.get('_source'))
        results.append(res)
    return results, es_results


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
def make_searchable(es_client, model):
    """Take a SQLAlchemy database model and add hook to make sure it is
       added, updated and remove for the Elastic Search Models. Also adds the
       classmehod 'es_search' for simple searching.

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
