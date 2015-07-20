Snippets
========

[![Build Status](https://travis-ci.org/andytom/snippets.svg?branch=master)](https://travis-ci.org/andytom/snippets)


Overview
--------

Snippets is a simple Note taking application with Full Text Search.

It is based on the Python [Flask framework](http://flask.pocoo.org/), uses
[Bootstrap](http://getbootstrap.com/) to look nice,
[ElasticSearch](https://www.elastic.co/products/elasticsearch) for searching
and a database of your choice for storage.


Running Snippets
----------------
You can get Snippets up and running on [localhost:5000](http://localhost:5000/)
using the following instructions. The following assumes you have python,
pip, virtualenv, and virtualenvwrapper installed.

It also assumes that you have ElasticSearch installed and listening
on ```localhost:9200```. For more information about setting up ElasticSearch
see the
[ElasticSearch Docs](https://www.elastic.co/guide/en/elasticsearch/reference/current/index.html)

~~~ bash
$ git clone https://github.com/andytom/snippets.git
$ mkvirtualenv snippets
$ cd snippets
$ pip install -r requirements.txt
$ ./manage.py db upgrade
$ ./manage.py runserver
~~~


Testing
-------
You can run all the test locally using manage.py.

~~~
$ ./manage.py test
~~~


Database Management
-------------------
Changes to the Database schema are managed using [Flask-Migrate](https://flask-migrate.readthedocs.org/en/latest/).
You can read the full help via:

~~~
$ ./manage.py db --help
~~~


TODO
----
- [x] Write a README
- [ ] Add Doc strings
- [x] Write more tests
- [x] Automate pep8 testing
- [x] Syntax highlighing
- [x] Manage commands for the database
 - [x] Create Database
 - [x] Migrate schema
 - [x] Instructions in the README
- [ ] Manage commands for the index
 - [ ] Reindex all items
 - [ ] Reindex some items
 - [ ] Delete some items
 - [ ] Delete all items
 - [ ] Complete rebuild
- [ ] Add users and permissions
 - [ ] Add user registration, login, log out
 - [ ] Must be logged in to create
 - [ ] Only user or admin can delete or edit
 - [ ] Shared/not shared snippets?
 - [ ] Manage commands/Admin Page for Users
- [ ] Add a landing page
- [ ] Add help pages
 - [ ] What Markdown is supported
 - [ ] What queries are supported
- [ ] Custom Validator for search query
- [ ] Groups of snippets
- [ ] Production Deployment instructions
- [ ] Work out a better way to do searching
 - [ ] Snippet.es_search
 - [ ] Moching out for testing
- [ ] Look at duplication in templates
 - [ ] Rendering snippets

License
-------
Snippets is licensed under the MIT license (See LICENSE) for more details.

This doesn't include 3rd Party code in ```app/static/3rd_party```, these files
are licenced under their own licences.
