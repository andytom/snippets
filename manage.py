#!/usr/bin/env python
import os
import sys
import unittest
from flask.ext.script import Manager, Server, Shell
from flask.ext.migrate import MigrateCommand
from app import app, db, Snippet


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
# Shell
#-----------------------------------------------------------------------------#
def _make_context():
    return dict(app=app, db=db, Snippet=Snippet)

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


#-----------------------------------------------------------------------------#
# Main
#-----------------------------------------------------------------------------#
if __name__ == '__main__':
    manager.run()
