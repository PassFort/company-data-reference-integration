from unittest import TestCase, skip
import requests
import time

API_URL = 'http://localhost:8001'

TEST_API_KEY = 'a4364e62-e58b-4b64-9c71-faead5417557'
TEST_API_SECRET = '/NoVqWHBRv23t5ae9OuQlODUX5yoAcJcFP8Z2nJldBkrsTCdqhRzGzrrTvD9EVqLgwTrXC4xKZ/Khfv6shMwAA=='
TEST_GROUP_ID = '418f28a7-b9c9-4ae4-8530-819c61b1ca6c'

GOOD_CREDENTIALS = {
    "api_key": TEST_API_KEY,
    "api_secret": TEST_API_SECRET,
    "is_pilot": True
}

PERSONAL_DETAILS_TM = {
    "name": {
        "given_names": ["Theresa"],
        "family_name": "May"
    }
}


class WorldCheckScreenCase(TestCase):

    def test_does_not_error_on_rogue_field(self):
        response = requests.post(API_URL + '/screening_request', json={
            "config": {
                "group_id": TEST_GROUP_ID
            },
            "credentials": GOOD_CREDENTIALS,
            "input_data": {
                "rogue": "Super rogue field",
                "entity_type": "INDIVIDUAL",
                "personal_details": PERSONAL_DETAILS_TM
            }
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['errors'], [])

    def test_bad_entity(self):
        response = requests.post(API_URL + '/screening_request', json={
            "config": {
                "group_id": TEST_GROUP_ID
            },
            "credentials": GOOD_CREDENTIALS,
            "input_data": {
                "entity_type": "NOT_AN_ENTITY",
                "personal_details": PERSONAL_DETAILS_TM
            }
        })
        result = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['errors'][0]['message'], 'Bad API request')
        self.assertEqual(result['errors'][0]['code'], 201)
        self.assertDictEqual(
            result['errors'][0]['info'],
            {
                "input_data": {
                    "entity_type": [
                        "Value must be one of ['INDIVIDUAL', 'COMPANY']."
                    ]
                }
            })

    def test_no_personal_details(self):
        response = requests.post(API_URL + '/screening_request', json={
            "config": {
                "group_id": TEST_GROUP_ID
            },
            "credentials": GOOD_CREDENTIALS,
            "input_data": {
                "entity_type": "INDIVIDUAL"
            }
        })
        result = response.json()
        self.assertEqual(response.status_code, 400)
        self.assertEqual(result['errors'][0]['message'], 'Bad API request')
        self.assertEqual(result['errors'][0]['code'], 201)
        self.assertDictEqual(
            result['errors'][0]['info'],
            {
                "input_data": {
                    "personal_details": [
                        "Personal details are required for individuals"
                    ]
                }
            })

    def test_bad_group_id(self):
        response = requests.post(API_URL + '/screening_request', json={
            "config": {
                "group_id": "abcdefg"
            },
            "credentials": GOOD_CREDENTIALS,
            "input_data": {
                "entity_type": "INDIVIDUAL",
                "personal_details": PERSONAL_DETAILS_TM
            }
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()

        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['errors'][0]['code'], 303)
        self.assertEqual(result['errors'][0]['message'], 'The provider cannot return a response for the specified id')

    def test_bad_authentication(self):
        response = requests.post(API_URL + '/screening_request', json={
            "config": {
                "group_id": "abcdefg"
            },
            "credentials": {
                "api_key": "123",
                "api_secret": "1234",
                "is_pilot": True
            },
            "input_data": {
                "entity_type": "INDIVIDUAL",
                "personal_details": PERSONAL_DETAILS_TM
            }
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result['errors']), 1)
        self.assertEqual(result['errors'][0]['code'], 303)
        self.assertEqual(result['errors'][0]['message'], 'The request has failed an authorisation check')

    def test_individual_successful_screening_request(self):

        with self.subTest('starts the screening succesfully'):
            response = requests.post(API_URL + '/screening_request', json={
                "config": {
                    "group_id": TEST_GROUP_ID
                },
                "credentials": GOOD_CREDENTIALS,
                "input_data": {
                    "entity_type": "INDIVIDUAL",
                    "personal_details": PERSONAL_DETAILS_TM
                }
            })

            self.assertEqual(response.status_code, 200)
            result = response.json()

            self.assertEqual(result['errors'], [])
            case_system_id = result['output_data']['worldcheck_system_id']

            self.assertIsNotNone(case_system_id)

        with self.subTest('gets the results from worldcheck'):
            retries = 60

            while retries > 0:
                response = requests.post(API_URL + '/results/' + case_system_id, json={
                    "credentials": GOOD_CREDENTIALS
                })

                if response.status_code != 202:
                    break
                retries -= 1
                time.sleep(1)

            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(result['errors'], [])
            self.assertGreater(len(result['raw']), 0)

    @skip('to be implemented')
    def test_company_successful_screening_request(self):
        pass
