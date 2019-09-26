from flask import request, wrappers
import unittest
import json
from app.application import app


API_URL = 'http://localhost:8001'


class IovationTestExamples(unittest.TestCase):
    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    def test_demo_deny_response(self):
        request = {
            'input_data': {
                'device_metadata': {
                    'token': 'BLACKBOX_FAIL',
                    'stated_ip': '1.1.1.1',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }
            },
            'credentials': {
                'subscriber_id': '12345678',
                'subscriber_account': 'test_account',
                'password': 'password'
            },
            'is_demo': True
        }

        response = self.testing_app.post('/run_check', content_type='application/json', json=request)

        response_json = json.loads(response.data)

        expected_output = {
            "device_metadata": {
                "token": "BLACKBOX_FAIL",
                "stated_ip": "1.1.1.1",
                "action": "new_account",
                "reference_id": "REF_ID",
                "device_id": "10003920005100080",
                "device_type": "WINDOWS"
            },
            "device_fraud_detection": {
                "provider_reference": "2000040009070100",
                "recommendation": "Deny",
                "recommendation_reason": "Evidence found",
                "total_score": -150,
                "matched_rules": [{
                    "name": "Evidence Exists",
                    "reason": "Evidence found",
                    "score": -100
                },{
                    "name": "More evidence",
                    "reason": "More evidence found",
                    "score": -50
                }]
            },
            "ip_location": {
                "ip_address": "74.121.28.132",
                "country": "USA",
                "region": "OREGON",
                "city": "PORTLAND" }
        }

        print(response_json)
        self.maxDiff = None
        self.assertEqual(expected_output, response_json['output_data'])
        self.assertIsNotNone(response_json['raw_data'])

    def test_demo_allow_response(self):
        request = {
            'input_data': {
                'device_metadata': {
                    'token': 'BLACKBOX',
                    'stated_ip': '1.1.1.1',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }
            },
            'credentials': {
                'subscriber_id': '12345678',
                'subscriber_account': 'test_account',
                'password': 'password'
            },
            'is_demo': True
        }

        response = self.testing_app.post('/run_check', content_type='application/json', json=request)

        response_json = json.loads(response.data)

        self.assertEqual('Allow', response_json['output_data']['device_fraud_detection']['recommendation'])

    def test_demo_review_response(self):
        request = {
            'input_data': {
                'device_metadata': {
                    'token': 'BLACKBOX_REFER',
                    'stated_ip': '1.1.1.1',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }
            },
            'credentials': {
                'subscriber_id': '12345678',
                'subscriber_account': 'test_account',
                'password': 'password'
            },
            'is_demo': True
        }

        response = self.testing_app.post('/run_check', content_type='application/json', json=request)

        response_json = json.loads(response.data)

        self.assertEqual('Review', response_json['output_data']['device_fraud_detection']['recommendation'])

    def test_response_using_test_account(self):
        request = {
            'input_data': {
                'device_metadata': {
                    'token': 'BLACKBOX',
                    'stated_ip': '1.1.1.1',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }
            },
            'credentials': {
                'subscriber_id': '388702',
                'subscriber_account': 'OLTP',
                'password': 'CRJSGGFH',
                'use_test_environment': True
            }
        }

        response = self.testing_app.post('/run_check', content_type='application/json', json=request)

        response_json = json.loads(response.data)

        self.assertEqual('Allow', response_json['output_data']['device_fraud_detection']['recommendation'])

    def test_response_without_blackbox(self):
        request = {
            'input_data': {
                'device_metadata': {
                    'token': '',
                    'stated_ip': '1.1.1.1',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }
            },
            'credentials': {
                'subscriber_id': '388702',
                'subscriber_account': 'OLTP',
                'password': 'CRJSGGFH',
                'use_test_environment': True
            }
        }

        response = self.testing_app.post('/run_check', content_type='application/json', json=request)

        response_json = json.loads(response.data)

        self.assertEqual('Allow', response_json['output_data']['device_fraud_detection']['recommendation'])
