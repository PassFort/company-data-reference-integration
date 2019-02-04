import requests
import unittest

API_URL = 'http://localhost:8001'


class TestApiValidation(unittest.TestCase):

    def assert_ekyc_request_returns(self, credentials, expected_status, expected_errors, is_demo=False):
        response = requests.post(
            f'{API_URL}/ekyc-check',
            json={
                'credentials': credentials,
                'is_demo': is_demo
            })
        self.assertEqual(response.status_code, expected_status)

        as_json = response.json()

        self.assertEqual(as_json['errors'], expected_errors)

    def test_expects_credentials_to_exist(self):
        self.assert_ekyc_request_returns(
            credentials={
            },
            expected_status=400,
            expected_errors=[
                {
                    'code': 201,
                    'info': {
                        'credentials': {
                            'customer_code': ['This field is required.'],
                            'customer_number': ['This field is required.'],
                            'security_code': ['This field is required.']
                        }
                    },
                    'message': 'Bad API request',
                    'source': 'API'
                }
            ]
        )
