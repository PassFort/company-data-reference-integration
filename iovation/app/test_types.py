from app.api.types import DeviceMetadata, IovationOutput, IovationCheckResponse
from app.request_handler import IovationHandler
from app.application import app
import json
import responses
from schematics.exceptions import DataError
import unittest


class TestInputData(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    def test_invalid_input(self):
        response = self.testing_app.post('/run_check', content_type='application/json', json={
            'input_data': {
                'device_metadata': [{
                    'token': 'BLACKBOX',
                    'stated_ip': '123.12.12.123',
                    'action': 'new_account',
                    'reference_id': 'REF_ID'
                }]
            },
            'is_demo': True
        })

        self.assertEqual(400, response.status_code)


    def test_as_iovation_device_data(self):
        device_data = DeviceMetadata({
            'token': 'BLACKBOX',
            'stated_ip': '123.12.12.123',
            'action': 'new_account',
            'reference_id': 'REF_ID'
        })

        iovation_device = device_data.as_iovation_device_data()

        self.assertEqual('BLACKBOX', iovation_device.blackbox)
        self.assertEqual('123.12.12.123', iovation_device.statedip)
        self.assertEqual('new_account', iovation_device.type)
        self.assertEqual('REF_ID', iovation_device.account_code)


    def test_input_without_optional_fields(self):
        device_data = DeviceMetadata({
            'token': 'BLACKBOX',
            'action': 'new_account'
        })

        iovation_device = device_data.as_iovation_device_data()

        self.assertEqual('BLACKBOX', iovation_device.blackbox)
        self.assertEqual(None, iovation_device.statedip)
        self.assertEqual('new_account', iovation_device.type)
        self.assertEqual(None, iovation_device.account_code)


class TestOutputData(unittest.TestCase):

    def test_deny_output(self):
        input_data = DeviceMetadata({
            'token': 'BLACKBOX',
            'stated_ip': '123.12.12.123',
            'action': 'new_account',
            'reference_id': 'REF_ID'
        })

        test_response = {
            "id": "06511936-8623-3cd4-b70f-6b852f7582f2",
            "result": "D",
            "reason": "Evidence found",
            "statedIp": "1.1.1.1",
            "accountCode": "REF_ID",
            "trackingNumber": 2000040009070100,
            "details": {
                "device": {
                    "alias": 10003920005100080,
                    "blackboxMetadata": {
                        "age": 16,
                        "timestamp": "2018-04-24T05:02:08Z"
                    },
                    "browser": {
                        "cookiesEnabled": True,
                        "configuredLanguage": "EN-US,EN;Q=0.9",
                        "flash": {
                            "installed": True,
                            "version": "29.0.0"
                            },
                        "language": "EN-US",
                        "type": "CHROME",
                        "timezone": "480",
                        "version": "65.0.3325.181"
                        },
                    "firstSeen": "2017-02-16T20:15:17.801Z",
                    "isNew": False,
                    "os": "WINDOWS NT 10.0",
                    "registrationResult": {
                        "matchStatus": "NONE_REGISTERED"
                        },
                    "screen": "1080X1920",
                    "type": "WINDOWS"
                },
                "statedIp": {
                    "address": "1.1.1.1",
                    "isp": "CLOUDFLARE INC",
                    "ipLocation": {
                        "city": "BRISBANE",
                        "country": "AUSTRALIA",
                        "countryCode": "AU",
                        "latitude": -27.46758,
                        "longitude": 153.02789,
                        "region": "QUEENSLAND",
                        "botnet": {
                            "intensity": 1,
                            "score": 9,
                            "lastSeen": "2019-04-09T06:19:18.000Z"
                            }
                        },
                    "parentOrganization": "APNIC AND CLOUDFLARE DNS RESOLVER PROJECT",
                    "source": "subscriber"
                },
                "realIp": {
                    "address": "74.121.28.132",
                    "isp": "IOVATION INC.",
                    "ipLocation": {
                        "city": "PORTLAND",
                        "country": "UNITED STATES",
                        "countryCode": "US",
                        "latitude": 45.51815,
                        "longitude": -122.67416,
                        "region": "OREGON",
                        "botnet": {
                            "intensity": 1,
                            "score": 9,
                            "lastSeen": "2019-04-09T06:19:18.000Z"
                            }
                        },
                    "parentOrganization": "IOVATION INC.",
                    "source": "iovation"
                },
                "ruleResults": {
                    "score": -150,
                    "rulesMatched": 2,
                    "rules": [ {
                        "type": "Evidence Exists",
                        "reason": "Evidence found",
                        "score": -100
                    },{
                        "type": "More evidence",
                        "reason": "More evidence found",
                        "score": -50
                    }]
                }
            }
        }

        raw_response, response_model = IovationOutput.from_json(test_response)

        output = IovationCheckResponse.from_iovation_output(response_model, input_data)

        expected_output = {
            "device_metadata": {
                "token": "BLACKBOX",
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
                "city": "PORTLAND"
            }
        }
        self.assertEqual(expected_output, output.to_primitive())

    def test_allow_output(self):
        input_data = DeviceMetadata({
            'token': 'BLACKBOX',
            'stated_ip': '123.12.12.123',
            'action': 'new_account',
            'reference_id': 'REF_ID'
        })

        test_response = {
            "id": "06511936-8623-3cd4-b70f-6b852f7582f2",
            "result": "A",
            "reason": "No evidence found",
            "statedIp": "1.1.1.1",
            "accountCode": "REF_ID",
            "trackingNumber": 2000040009070100,
            "details": {
                "device": {
                    "blackboxMetadata": {
                        "age": 16,
                        "timestamp": "2018-04-24T05:02:08Z"
                    },
                    "browser": {
                        "cookiesEnabled": True,
                        "configuredLanguage": "EN-US,EN;Q=0.9",
                        "flash": {
                            "installed": True,
                            "version": "29.0.0"
                            },
                        "language": "EN-US",
                        "type": "CHROME",
                        "timezone": "480",
                        "version": "65.0.3325.181"
                        },
                    "firstSeen": "2017-02-16T20:15:17.801Z",
                    "isNew": False,
                    "os": "WINDOWS NT 10.0",
                    "registrationResult": {
                        "matchStatus": "NONE_REGISTERED"
                        },
                    "screen": "1080X1920",
                    "type": "WINDOWS"
                },
                "realIp": {
                    "isp": "IOVATION INC.",
                    "address": "74.121.28.132",
                    "ipLocation": {
                        "latitude": 45.51815,
                        "longitude": -122.67416,
                        "region": "OREGON",
                        "botnet": {
                            "intensity": 1,
                            "score": 9,
                            "lastSeen": "2019-04-09T06:19:18.000Z"
                            }
                        },
                    "parentOrganization": "IOVATION INC.",
                    "source": "iovation"
                },
                "ruleResults": {
                    "score": -150,
                    "rulesMatched": 2,
                    "rules": [ {
                        "type": "Evidence Exists",
                        "reason": "Evidence found",
                        "score": -100
                    },{
                        "type": "More evidence",
                        "reason": "More evidence found",
                        "score": -50
                    }]
                }
            }
        }

        raw_response, response_model = IovationOutput.from_json(test_response)

        output = IovationCheckResponse.from_iovation_output(response_model, input_data)

        expected_output = {
            "device_metadata": {
                "token": "BLACKBOX",
                "stated_ip": "1.1.1.1",
                "action": "new_account",
                "reference_id": "REF_ID",
                "device_id": None,
                "device_type": "WINDOWS"
            },
            "device_fraud_detection": {
                "provider_reference": "2000040009070100",
                "recommendation": "Allow",
                "recommendation_reason": "No evidence found",
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
                "country": None,
                "region": "OREGON",
                "city": None
            }
        }
        self.assertEqual(expected_output, output.to_primitive())


    def test_credentials(self):
        test_credentials = {
            'subscriber_id': '388702',
            'subscriber_account': 'OLTP',
            'password': 'CRJSGGFH',
            'use_test_environment': True
        }

        test_handler = IovationHandler(test_credentials)

        token = test_handler.get_authorization_token()

        self.assertEqual('Mzg4NzAyL09MVFA6Q1JKU0dHRkg=', token)
        self.assertEqual('https://ci-api.iovation.com/fraud/v1', test_handler.base_url)

        credentials = {
            'subscriber_id': '388702',
            'subscriber_account': 'OLTP',
            'password': 'CRJSGGFH',
            'use_test_environment': False
        }

        handler = IovationHandler(credentials)
        self.assertEqual('https://api.iovation.com/fraud/v1', handler.base_url)

    def test_no_test_flag(self):
        credentials = {
            'subscriber_id': '388702',
            'subscriber_account': 'OLTP',
            'password': 'CRJSGGFH'
        }

        handler = IovationHandler(credentials)
        self.assertEqual('https://api.iovation.com/fraud/v1', handler.base_url)

