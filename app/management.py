from __future__ import unicode_literals
from flask.ext.script import Manager, prompt_bool
from app import es, Snippet
from make_searchable import do_index_item, do_delete_item


#-----------------------------------------------------------------------------#
# Manager setup
#-----------------------------------------------------------------------------#
es_manager = Manager(usage="Perform ElasticSearch Operations")


#-----------------------------------------------------------------------------#
# Management commands
#-----------------------------------------------------------------------------#
@es_manager.command
def ping():
    "Test the connection to ElasticSearch"
    print "Trying to connect to ElasticSearch...",
    if es.ping():
        print "Connected to ElasticSearch OK!"
    else:
        print "Unable to connect to ElasticSearch!"


@es_manager.command
def reindex(snippet_id):
    "Reindex one Snippets"
    snippet = Snippet.query.get(snippet_id)

    if snippet:
        do_index_item(es, snippet)
        print "Snippet '{} - {}' has been reindexed".format(snippet.id,
                                                            snippet.title)
    else:
        print "No Snippet with id '{}' to index".format(snippet_id)


@es_manager.command
def delete(snippet_id):
    "Remove one snippet from the index"
    do_delete_item(es, Snippet, snippet_id)
    print "Snippet '{}' has been deleted from the index".format(snippet_id)


@es_manager.command
def rebuild():
    "Remove and reindex all Snippets"
    if prompt_bool(
            "Are you sure you want to rebuild the index"):
        es.delete_by_query(index=Snippet.__es_index__,
                           doc_type=Snippet.__es_doc_type__,
                           q='*')
        print "All items deleted from the index"
        for snippet in Snippet.query.all():
            do_index_item(es, snippet)
            print "Snippet '{} - {}' has been reindexed".format(snippet.id,
                                                                snippet.title)
