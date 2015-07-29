import elasticsearch
from sqlalchemy import event


#-----------------------------------------------------------------------------#
# Helpers
#-----------------------------------------------------------------------------#
def do_index_item(es_client, item):
    """do_index_item

       Take the passed item and add it to the index using the passed
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
    """do_delete_item

       Remove a document from the ElasticSearch index.

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


#-----------------------------------------------------------------------------#
# Main
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
        do_index_item(es_client, target)

    def delete_item(mapper, connection, target):
        do_delete_item(es_client, model, target)

    event.listen(model, 'after_insert', index_item)
    event.listen(model, 'after_update', index_item)
    event.listen(model, 'after_delete', delete_item)
