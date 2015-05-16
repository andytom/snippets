import os
import unittest
from flask.ext.script import Manager, Server
from app import app


manager = Manager(app)


server = Server(host='0.0.0.0')
manager.add_command("runserver", server)


@manager.command
def test():
    """Runs all the tests"""
    parent_dir = os.path.dirname(os.path.abspath(__file__))
    app_dir = os.path.join(parent_dir, 'app')
    tests = unittest.TestLoader().discover(app_dir)
    results = unittest.TextTestRunner(verbosity=2).run(tests)


if __name__ == '__main__':
    manager.run()
