import requests
import unittest
import json
from app.api.mock_data.mock_requests import successful_work_request, successful_study_request, \
    unidentified_person_request, no_visa_request, login_error_request
from app.api.mock_data.mock_responses import no_visa_response, login_error_response, \
     successful_work_response, successful_study_response

API_URL = 'http://localhost:8001'

@unittest.skip
class VSureTestExamples(unittest.TestCase):

    def test_successful_response(self):
        response = requests.post(f'{API_URL}/visa-check', json=successful_work_request)

        response_json = response.json()

        self.assertEqual(successful_work_response, response_json['output_data'])

    def test_successful_study_response(self):
        response = requests.post(f'{API_URL}/visa-check', json=successful_study_request)

        response_json = response.json()

        self.assertEqual(successful_study_response, response_json['output_data'])

    def test_unidentified_person(self):
        response = requests.post(f'{API_URL}/visa-check', json=unidentified_person_request)

        response_json = response.json()

        self.assertEqual(303, response_json['errors'][0]['code'])
        self.assertEqual('Could not complete visa check - The Department has not been able to identify the person. Please check that the details you entered in are correct.', response_json['errors'][0]['message'])
        self.assertEqual('PROVIDER', response_json['errors'][0]['source'])

    def test_no_visa(self):
        response = requests.post(f'{API_URL}/visa-check', json=no_visa_request)

        response_json = response.json()

        self.assertEqual(no_visa_response, response_json['output_data'])
