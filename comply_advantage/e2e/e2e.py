import requests
import unittest

API_URL = 'http://localhost:8001'


class TestApiValidation(unittest.TestCase):

    def assert_screening_request_returns(self, input_data, expected_status, expected_errors, is_demo=False):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                "credentials": {"api_key": "test"},
                "config": {},
                "input_data": input_data,
                "is_demo": is_demo
            })
        self.assertEqual(response.status_code, expected_status)

        as_json = response.json()

        self.assertEqual(as_json['errors'], expected_errors)

    def test_expects_individual_data_to_exist(self):
        self.assert_screening_request_returns(
            input_data={
                "entity_type": "INDIVIDUAL"
            },
            expected_status=400,
            expected_errors=[
                {
                    "code": 201,
                    "info": {
                        "input_data": {
                            "personal_details": [
                                "Personal details are required for individuals"
                            ]
                        }
                    },
                    "message": "Bad API request",
                    "source": "API"
                }
            ]
        )

    def test_expects_company_data_to_exist(self):
        self.assert_screening_request_returns(
            input_data={
                "entity_type": "COMPANY"
            },
            expected_status=400,
            expected_errors=[
                {
                    "code": 201,
                    "info": {
                        "input_data": {
                            "metadata": [
                                "Company metadata is required for companies"
                            ]
                        }
                    },
                    "message": "Bad API request",
                    "source": "API"
                }
            ]
        )

    def test_accepts_partial_dates_as_dob(self):

        for dob in ["1989", "1989-01", "1989-01-02"]:
            with self.subTest(f"Accepts dob as {dob}"):
                self.assert_screening_request_returns(
                    input_data={
                        "entity_type": "INDIVIDUAL",
                        "personal_details": {
                            "name": {
                                "family_name": "Hussein",
                                "given_names": ["Hugo"]
                            },
                            "dob": dob
                        }
                    },
                    expected_status=200,
                    expected_errors=[],
                    is_demo=True
                )

        with self.subTest('expects a valid date'):
            self.assert_screening_request_returns(
                input_data={
                    "entity_type": "INDIVIDUAL",
                    "personal_details": {
                        "name": {
                            "family_name": "Hussein",
                            "given_names": ["Hugo"]
                        },
                        "dob": "1989-00"
                    }
                },
                expected_status=400,
                expected_errors=[
                    {
                        "code": 201,
                        "info": {
                            "input_data": {
                                "personal_details": {
                                    "dob": [
                                        "Could not parse 1989-00. Valid formats: %Y, %Y-%m, %Y-%m-%d"
                                    ]
                                }
                            }
                        },
                        "message": "Bad API request",
                        "source": "API"
                    }
                ],
                is_demo=True
            )
