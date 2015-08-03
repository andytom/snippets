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


# TODO - Work out a better way to search for results
def es_search(cls, es, q):
    """Search over the item

       :param es: The ElasticSearch client that we want to use for
                  searching.
       :param q: The query in Lucene Query Language to search ElasticSearch

       :returns: A list containing the results of the search. Each result
                 is a dict containing the id, title and text of the Snippet
    """
    es_results = es.search(index=cls.__es_index__,
                           doc_type=cls.__es_doc_type__,
                           q=q)
    results = []
    for hit in es_results.get('hits', {}).get('hits', []):
        res = {'id': hit.get('_id')}
        res.update(hit.get('_source'))
        results.append(res)
    return results


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
def make_searchable(es_client, model):
    """Take a SQLAlchemy database model and add hook to make sure it is
       add, updated and remove for the Elastic Search Models.

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

    model.es_search = classmethod(es_search)
