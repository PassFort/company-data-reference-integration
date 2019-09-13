import unittest
import requests

API_URL = 'http://localhost:8001'

CREDENTIALS = {
    "api_key": "60b5b1c4-3a08-4cc2-b"
}


class CharitiesTests(unittest.TestCase):

    def test_macmillan_gbr(self):
        response = requests.post(API_URL + '/charity-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": "GBR",
                    "number": "09565115",
                    "name": "Macmillan Cancer Support",
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()

        trustees = result['output_data']['officers']['trustees']

        self.assertEqual(response.status_code, 200)
        self.assertTrue(len(trustees) >= 10)
        self.assertEqual(result['output_data']['metadata']['uk_charity_commission_number'], '261017')

    def test_freeman_gbr(self):
        response = requests.post(API_URL + '/charity-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": "GBR",
                    "number": "CE002298",
                    "name": "FREEMAN HEART & LUNG TRANSPLANT ASSOCIATION",
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()

        trustees = result['output_data']['officers']['trustees']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['output_data']['metadata']['uk_charity_commission_number'], '1157894')
        self.assertTrue(len(trustees) > 5)


class CharitiesErrorHandlingTests(unittest.TestCase):

    def test_missing_name(self):
        response = requests.post(API_URL + '/charity-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": "GBR",
                    "number": "CE002298",
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['errors'][0]['message'], 'Missing company name in input')
        self.assertEqual(len(result['errors']), 1)

    def test_missing_apikey(self):
        response = requests.post(API_URL + '/charity-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": "GBR",
                    "name": "Macmillan Cancer Support",
                    "number": "CE002298",
                }
            },
            "config": {},
            "credentials": {},
        })
        result = response.json()

        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['errors'][0]['message'], 'Missing apikey')
        self.assertEqual(len(result['errors']), 1)
