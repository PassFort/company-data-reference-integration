"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response from the provider
"""

import responses
import unittest


from .application import app
from .api.types import ErrorCode


class TestDemoData(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_allow(self):
        # TODO
        pass

    def test_deny(self):
        # TODO
        pass

    def test_review(self):
        # TODO
        pass
