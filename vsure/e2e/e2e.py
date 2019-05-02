from flask import request, wrappers
import unittest
import json
from app.application import app
from app.api.mock_data.mock_requests import successful_work_request, successful_study_request, \
    unidentified_person_request, no_visa_request, expired_request, no_expiry_request
from app.api.mock_data.mock_responses import no_visa_response, expired_response, no_expiry_response, \
    successful_work_response, successful_study_response, unidentified_person_response

API_URL = 'http://localhost:8001'


class VSureTestExamples(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    def test_successful_response(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=successful_work_request)

        response_json = json.loads(response.data)

        self.assertEqual(successful_work_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])

    def test_successful_study_response(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=successful_study_request)

        response_json = json.loads(response.data)

        self.assertEqual(successful_study_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])

    def test_unidentified_person(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=unidentified_person_request)

        response_json = json.loads(response.data)

        self.assertEqual(unidentified_person_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])

    def test_no_visa(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=no_visa_request)

        response_json = json.loads(response.data)

        self.assertEqual(no_visa_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])

    def test_no_expiry_visa(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=no_expiry_request)

        response_json = json.loads(response.data)

        self.assertEqual(no_expiry_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])

    def test_expired_visa(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json=expired_request)

        response_json = json.loads(response.data)

        self.assertEqual(expired_response, response_json['output_data']['visa_check'])
        self.assertIsNotNone(response_json['raw'])
