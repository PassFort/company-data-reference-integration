import requests
import unittest
import json
from app.api.mock_data.mock_requests import mock_successful_request, mock_unidentified_person_request
from app.api.mock_data.mock_responses import mock_successful_response

API_URL = 'http://localhost:8001'

class Test(unittest.TestCase):

    def test_successful_response(self):
        response = requests.post(f'{API_URL}/visa-check', json=mock_successful_request)

        response_json = response.json()

        self.assertEqual(mock_successful_response, response_json['output_data'])

    def test_unidentified_person(self):
    	response = requests.post(f'{API_URL}/visa-check', json=mock_unidentified_person_request)

    	response_json = response.json()
    	print(response_json)
    	self.assertEqual('', response_json)
