Snippets
========

[![Build Status](https://travis-ci.org/andytom/snippets.svg?branch=master)](https://travis-ci.org/andytom/snippets)

Overview
--------
Snippets is a simple note taking application with Full Text Search.

It is based on the Python [Flask framework](http://flask.pocoo.org/), uses
[Bootstrap](http://getbootstrap.com/) to look nice,
[ElasticSearch](https://www.elastic.co/products/elasticsearch) for searching
and a database of your choice for storage.

Running Snippets
----------------
You can get Snippets up and running on [localhost:5000](http://localhost:5000/)
using the following instructions. The following assumes you have [git](https://git-scm.com/),
[python](https://www.python.org/), [pip](https://docs.python.org/2.7/installing/),
[virtualenv](https://virtualenv.pypa.io/en/latest/),
and [virtualenvwrapper](https://virtualenvwrapper.readthedocs.org/en/latest/) installed.

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

As well as test for pep8.

~~~
$ ./manage.py pep8
~~~

Management Commands
-------------------

### Database Management
Changes to the Database schema are managed using [Flask-Migrate](https://flask-migrate.readthedocs.org/en/latest/).
You can read the full help via:

~~~
$ ./manage.py db --help
~~~

### ElasticSearch Index Management
The connection to ElasticSearch and the ElasticSearch Indexes can be managed using manage.py.
You can read the full help via:

~~~
$ ./manage.py es --help
~~~

### User Management
You can add or delete users using the manage.py script.
You can read the full help via:

~~~
$ ./manage.py user --help
~~~

TODO
----
- [x] Write a README
- [x] Add Doc strings
- [x] Write more tests
- [x] Automate pep8 testing
- [x] Syntax highlighing
- [x] Manage commands for the database
- [x] Manage commands for the index
- [x] Add users
- [x] Look at duplication in templates
- [x] Preview for Markdown on Create/Edit Snippts
- [ ] Intergrate Users
 - [ ] Add link to login/register
 - [ ] Connect users and snippets
- [ ] Add permissions
 - [ ] Must be logged in to create
 - [ ] Only owning user or admin can delete or edit
 - [ ] Shared/not shared snippets?
- [ ] Replce index with a landing page
- [ ] Add help pages
 - [ ] What Markdown is supported
 - [ ] What queries are supported
- [ ] Custom Validators
 - [ ] Search query
 - [x] Add user (unique username)
- [ ] Groups of snippets
- [ ] Production Deployment instructions
- [ ] Work out a better way to do searching
 - [x] Snippet.es_search
 - [ ] Moching out for testing (vcrpy?)
 - [x] Return list of Snippets
- [ ] Tests for make_searchable
- [ ] Logging
- [ ] Admin Page for Users
- [ ] Add created and updated dates to Snippets

License
-------
Snippets is licensed under the MIT license (See LICENSE) for more details.

This doesn't include 3rd Party code in ```app/static/3rd_party```, these files
are licenced under their own licences.
