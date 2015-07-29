#!/usr/bin/env python
from __future__ import unicode_literals
import os
import sys
import subprocess
import unittest
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import MigrateCommand
from app import app, db, es, Snippet
from app.management import es_manager


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
# ElasticSearch Manage
#-----------------------------------------------------------------------------#
manager.add_command('es', es_manager)


#-----------------------------------------------------------------------------#
# Shell
#-----------------------------------------------------------------------------#
def _make_context():
    """_make_context

       :returns: A dict of objects to import in the shell
    """
    return dict(app=app, db=db, es=es, Snippet=Snippet)

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
    """Run all pep8 tests"""

    command = subprocess.Popen(["pep8", "--statistics", "--show-source"])

    command.communicate()
    sys.exit(command.returncode)


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    manager.run()
