from app.api.mock_data.mock_request import mock_request
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

    @responses.activate
    def test_successful_post(self):
        responses.add(responses.POST,
            'https://api.vsure.com.au/v1/visacheck?type=json&json={"key":"JtGXbnOxncr1MZZ","visachecktype":"WORK",visaholder":{"given_names":"John","family_name":"Smith","date_of_birth": "2000-01-01","passport_id":"77777777","country": "IND"}}'
        )

        response = self.testing_app.post('/visa-check',
            data=json.dumps(mock_request),
            content_type='application/json'
        )

        self.assertEqual(200, response.status_code)
