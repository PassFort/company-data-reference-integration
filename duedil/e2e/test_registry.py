import unittest
import requests

API_URL = 'http://localhost:8001'

CREDENTIALS = {
    "auth_token": "f1137e75bf253e6eb4231a9a09b5a76d"
}

GLOBAL_COVERAGE = {
    "has_global_coverage": True
}


class RegistryTests(unittest.TestCase):

    def test_health_endpoint(self):
        response = requests.get(API_URL + '/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'success')

    def test_passfort_gbr(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "GBR"
                    },
                    "number": {
                        "v": "09565115"
                    }
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['output_data']['metadata']['incorporation_date']['v'], '2015-04-28')
        self.assertTrue(len(result['output_data']['officers']['directors']), 3)

    def test_axa_fr(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "FRA"
                    },
                    "number": {
                        "v": "572093920"
                    }
                }
            },
            "config": GLOBAL_COVERAGE,
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['output_data']['metadata']['incorporation_date']['v'], '1957-01-01')
        self.assertTrue(len(result['output_data']['officers']['directors']), 3)

    def test_boylesports_irl(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "IRL"
                    },
                    "number": {
                        "v": "194670"
                    }
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(result['output_data']['metadata']['incorporation_date']['v'], '1992-10-21')
        self.assertTrue(len(result['output_data']['officers']['directors']), 3)

    def test_bad_company_number(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "GBR"
                    },
                    "number": {
                        "v": "57209aa920"
                    }
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertIs(result.get('output_data', None), None)
        self.assertIs(result.get('raw', None), None)

    def test_no_global_coverage(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "FRA"
                    },
                    "number": {
                        "v": "572093920"
                    }
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(
            result['errors'][0]['message'],
            'Country \'FRA\' is not supported by the provider for this stage'
        )

    def test_with_global_coverage(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "FRA"
                    },
                    "number": {
                        "v": "572093920"
                    }
                }
            },
            "config": GLOBAL_COVERAGE,
            "credentials": CREDENTIALS,
        })
        result = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(result['errors']), 0)
