import requests
import unittest

API_URL = 'http://localhost:8001'

test_address_history = [
    {
        'address': {
            'state_province': 'ON',
            'postal_code': 'abcde',
            'locality': 'qwerty'
        }
    }
]


class TestApiValidation(unittest.TestCase):

    def assert_ekyc_request_returns(self, credentials, input_data, expected_status, expected_errors, is_demo=False):
        json_body ={
            'credentials': credentials,
            'is_demo': is_demo
        }
        if input_data:
            json_body['input_data'] = input_data

        response = requests.post(
            f'{API_URL}/ekyc-check',
            json=json_body)
        self.assertEqual(response.status_code, expected_status)

        as_json = response.json()

        self.assertEqual(as_json['errors'], expected_errors)

        return as_json

    def test_expects_credentials_to_exist(self):
        self.assert_ekyc_request_returns(
            credentials={},
            input_data={},
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

    def test_returns_demo_data_2_plus_2(self):
        result = self.assert_ekyc_request_returns(
            credentials={
                'customer_code': 'a',
                'customer_number': 'b',
                'security_code': 'c'
            },
            input_data={
                'personal_details': {
                    'name': {
                        'given_names': ['Tom'],
                        'family_name': 'Jones'
                    },
                    'dob': '1990'
                },
                'address_history': test_address_history
            },
            expected_status=200,
            expected_errors=[],
            is_demo=True
        )
        ekyc = result['output_data']['electronic_id_check']
        self.assertEqual(len(ekyc['matches']), 2)
        self.assertEqual(ekyc['rules'][0]['active'], True)
        self.assertEqual(ekyc['rules'][0]['result'], '2+2')

    def test_returns_demo_data_1_plus_1(self):
        result = self.assert_ekyc_request_returns(
            credentials={
                'customer_code': 'a',
                'customer_number': 'b',
                'security_code': 'c'
            },
            input_data={
                'personal_details': {
                    'name': {
                        'given_names': ['Tom', '1+1'],
                        'family_name': 'Jones'
                    },
                    'dob': '1990'
                },
                'address_history': test_address_history
            },
            expected_status=200,
            expected_errors=[],
            is_demo=True
        )
        ekyc = result['output_data']['electronic_id_check']
        self.assertEqual(len(ekyc['matches']), 1)
        self.assertEqual(ekyc['rules'][1]['active'], True)
        self.assertEqual(ekyc['rules'][1]['result'], '1+1')

    def test_returns_demo_data_Fail(self):
        result = self.assert_ekyc_request_returns(
            credentials={
                'customer_code': 'a',
                'customer_number': 'b',
                'security_code': 'c'
            },
            input_data={
                'personal_details': {
                    'name': {
                        'given_names': ['Tom', 'Fail'],
                        'family_name': 'Jones'
                    },
                    'dob': '1990'
                },
                'address_history': test_address_history
            },
            expected_status=200,
            expected_errors=[],
            is_demo=True
        )
        ekyc = result['output_data']['electronic_id_check']
        self.assertEqual(len(ekyc['matches']), 0)
        self.assertEqual(ekyc['rules'][3]['active'], True)
        self.assertEqual(ekyc['rules'][3]['result'], 'Fail')
