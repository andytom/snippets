#!/usr/bin/env python
import os
import sys
import unittest
from flask.ext.script import Manager, Server
from app import app


manager = Manager(app)


server = Server(host='0.0.0.0', use_debugger=True)
manager.add_command("runserver", server)


@manager.command
def test():
    """Runs all the tests"""
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    test_dir = os.path.join(parent_dir, 'tests')
    tests = unittest.TestLoader().discover(test_dir)
    results = unittest.TextTestRunner(verbosity=2).run(tests)
    ret = not results.wasSuccessful()
    sys.exit(ret)


if __name__ == '__main__':
    manager.run()
