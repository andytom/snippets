#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
    manage.py
    ~~~~~~~~~
    Mangement commands for Snippets.

    :copyright: (c) 2015 by Thomas O'Donnell.
    :license: MIT, see LICENSE for more details.
"""
from __future__ import unicode_literals
import os
import sys
import subprocess
import unittest
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import MigrateCommand
from app import app, db, es
from app.management import es_manager, user_manager
from app.models import Snippet, User


manager = Manager(app)


#-----------------------------------------------------------------------------#
# Server
#-----------------------------------------------------------------------------#
server = Server(host='0.0.0.0', use_debugger=True)
manager.add_command("runserver", server)


#-----------------------------------------------------------------------------#
# Database Management
#-----------------------------------------------------------------------------#
manager.add_command('db', MigrateCommand)


#-----------------------------------------------------------------------------#
# ElasticSearch Management
#-----------------------------------------------------------------------------#
manager.add_command('es', es_manager)


#-----------------------------------------------------------------------------#
# User Management
#-----------------------------------------------------------------------------#
manager.add_command('user', user_manager)


#-----------------------------------------------------------------------------#
# Shell
#-----------------------------------------------------------------------------#
def _make_context():
    """Function to declare all the objects to import into the shell.

       :returns: A dict of objects to import in the shell
    """
    return dict(app=app, db=db, es=es, Snippet=Snippet, User=User)

manager.add_command("shell", Shell(make_context=_make_context))


#-----------------------------------------------------------------------------#
# Running Tests
#-----------------------------------------------------------------------------#
@manager.command
def test():
    """Runs all the tests"""
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(parent_dir, 'tests')

    tests = unittest.TestLoader().discover(test_dir)
    results = unittest.TextTestRunner(verbosity=2).run(tests)

    ret = not results.wasSuccessful()
    sys.exit(ret)


@manager.command
def pep8():
    """Run pep8 lint"""

    command = subprocess.Popen(["pep8", "--statistics", "--show-source"])

    command.communicate()
    if not command.returncode:
        print "pep8 OK!"
    sys.exit(command.returncode)


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    manager.run()
