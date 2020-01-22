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
                                        "Input is not valid date: 1989-00"
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

    def test_accepts_nationality(self):
        for nationality in ["esp", "zwe", "BAD_STRING"]:
            with self.subTest(f"Accepts nationality as {nationality}"):
                self.assert_screening_request_returns(
                    input_data={
                        "entity_type": "INDIVIDUAL",
                        "personal_details": {
                            "name": {
                                "family_name": "Mugabe",
                                "given_names": ["Robert"]
                            },
                            "nationality": nationality,
                            "dob": "1927"
                        }
                    },
                    expected_status=200,
                    expected_errors=[],
                    is_demo=True
                )

class TestEvents(unittest.TestCase):

    def test_on_peps_and_sanctions_only(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                "credentials": {"api_key": "test"},
                "config": {
                },
                "input_data": {
                    "entity_type": "INDIVIDUAL",
                    "personal_details": {
                        "name": {
                            "family_name": "Assad",
                            "given_names": ["Bashar"]
                        }
                    }
                },
                "is_demo": True
            })

        result = response.json()
        self.assertEqual(result["errors"], [])
        self.assertEqual(result["search_ids"], [80017938])
        self.assertEqual(response.status_code, 200)

        with self.subTest("Only returns pep and sanction events"):
            self.assertEqual(len(result["events"]), 2)
            pep_event = result["events"][0]
            sanction_event = result["events"][1]

            self.assertEqual(pep_event["event_type"], "PEP_FLAG")
            self.assertEqual(sanction_event["event_type"], "SANCTION_FLAG")

            with self.subTest("returns pep tier"):
                tier = pep_event["pep"]["tier"]
                self.assertEqual(tier, 1)

            with self.subTest("returns sanction lists"):
                sanction_list_names = sorted([s["list"] for s in sanction_event["sanctions"]])
                self.assertEqual(
                    sanction_list_names,
                    [
                        "DFAT Australia List",
                        "DFATD Canada Special Economic Measures Act Designations",
                        "Europe Sanctions List",
                        "France Liste Unique de Gels",
                        "HM Treasury List",
                        "OFAC SDN List",
                        "Swiss SECO List"
                    ]
                )

            with self.subTest("does not return adverse media in sources"):
                source_names = sorted(s['name'] for s in pep_event['sources'])
                self.assertEqual(
                    source_names,
                    [
                        'ComplyAdvantage PEP Data',
                        'Related Url',
                        'Related Url',
                        'Related Url',
                        'US System for Award Management Exclusions',
                        'company AM'
                    ]
                )

    def test_on_peps_sanctions_and_media(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                "credentials": {"api_key": "test"},
                "config": {
                    "include_adverse_media": True
                },
                "input_data": {
                    "entity_type": "INDIVIDUAL",
                    "personal_details": {
                        "name": {
                            "family_name": "Assad",
                            "given_names": ["Bashar"]
                        }
                    }
                },
                "is_demo": True
            })

        result = response.json()
        self.assertEqual(result["errors"], [])
        self.assertEqual(response.status_code, 200)

        with self.subTest("Also returns media"):
            self.assertEqual(len(result["events"]), 3)
            pep_event = result["events"][0]
            sanction_event = result["events"][1]
            media_event = result["events"][2]

            self.assertEqual(pep_event["event_type"], "PEP_FLAG")
            self.assertEqual(sanction_event["event_type"], "SANCTION_FLAG")
            self.assertEqual(media_event["event_type"], "ADVERSE_MEDIA_FLAG")

            with self.subTest("returns media"):
                self.assertEqual(len(media_event["media"]), 30)

            with self.subTest('returns adverse media in sources'):
                source_names = sorted(s['name'] for s in pep_event['sources'])
                self.assertEqual(
                    source_names,
                    [
                        'Adverse Media',
                        'ComplyAdvantage Adverse Media',
                        'ComplyAdvantage PEP Data',
                        'Related Url',
                        'Related Url',
                        'Related Url',
                        'US System for Award Management Exclusions',
                        'company AM'
                    ]
                )

