import flask_heroku_runner

import unittest

import os
import random

import mock


class HerokuEnvironmentTests(unittest.TestCase):

    @mock.patch('flask.Flask.run')
    def test_that_app_uses_port_envvar(self, run_method):
        some_number = int(random.uniform(2048, 10000))
        os.environ['PORT'] = str(some_number)
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(host='127.0.0.1')
        run_method.assert_called_with(host='127.0.0.1', port=some_number)

    @mock.patch('flask.Flask.run')
    def test_that_app_uses_host_envvar(self, run_method):
        random_ip = '{}.{}.{}.{}'.format(
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)),
            int(random.uniform(1, 254)))
        os.environ['HOST'] = random_ip
        app = flask_heroku_runner.HerokuApp(__name__)
        app.run(port=6543)
        run_method.assert_called_with(host=random_ip, port=6543)


def all_tests():
    return [HerokuEnvironmentTests()]

all_tests.__test__ = False

