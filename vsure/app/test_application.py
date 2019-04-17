from app.api.mock_data.mock_requests import mock_successful_request
from app.application import app
import json
import responses
import unittest


class TestHandleVisaRequest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    def test_validation_error(self):
        response = self.testing_app.post('/visa-check')

        self.assertEqual(400, response.status_code)
