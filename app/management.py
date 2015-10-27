# -*- coding: utf-8 -*-
"""
    Management
    ~~~~~~~~~~
    Custom Flask Script management commands for Snippets

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
from flask.ext.script import Manager, prompt_bool, prompt_pass, prompt
from app import es, Snippet, User, db
from make_searchable import do_index_item, do_delete_item


#-- ES Management commands ---------------------------------------------------#
es_manager = Manager(usage="Perform ElasticSearch Operations")


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


#-- User Management commands -------------------------------------------------#
user_manager = Manager(usage="Manage Users")


@user_manager.command
def add(username=None):
    "Add a new user"
    if username is None:
        username = prompt("Username")

    if User.query.filter_by(username=username).count():
        print "There is already a user with the username {}".format(username)
    else:
        password = prompt_pass('Password')
        confirm = prompt_pass('Confirm Password')
        if password == confirm:
            user = User(username, password)
            db.session.add(user)
            db.session.commit()
            print "Created user {}".format(user.username)
        else:
            print "Passwords don't match"


@user_manager.command
def delete(username):
    "Delete a user by username"
    user = User.query.filter_by(username=username).first()
    if user:
        if prompt_bool("Are you sure you want to delete {}".format(username)):
            db.session.delete(user)
            db.session.commit()
            print "User '{}' deleted".format(username)
    else:
        print "Unable to find User '{}'".format(username)
        print "Is that the correct username?"
