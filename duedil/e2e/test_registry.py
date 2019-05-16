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

    def test_director_and_secretary(self):
        response = requests.post(API_URL + '/registry-check', json={
            "input_data": {
                "metadata": {
                    "country_of_incorporation": {
                        "v": "GBR"
                    },
                    "number": {
                        "v": "04253482"
                    }
                }
            },
            "config": {},
            "credentials": CREDENTIALS,
        })

        result = response.json()
        self.assertEqual(response.status_code, 200)
        officers = result['output_data']['officers']
        self.assertGreater(len(officers['directors']), 0)
        self.assertGreater(len(officers['secretaries']), 0)
        self.assertGreater(len(officers['resigned']), 0)

        as_director = next(d for d in officers['directors'] if d['last_name']['v'] == 'Boys')
        as_secretary = next(d for d in officers['secretaries'] if d['last_name']['v'] == 'Boys')
        as_resigned = next(d for d in officers['resigned'] if d['last_name']['v'] == 'Boys')

        with self.subTest('is a director, not resigned'):
            self.assertEqual(as_director['appointed_on'], {
                "v": "2011-04-19"
            })
            self.assertEqual(as_director['original_role'], {
                "v": "Director"
            })
            self.assertFalse('resigned_on' in as_director)

        with self.subTest('is a resigned secretary'):
            self.assertEqual(as_secretary['appointed_on'], {
                "v": "2011-04-19"
            })
            self.assertEqual(as_secretary['original_role'], {
                "v": "Secretary"
            })
            self.assertEqual(as_secretary['resigned_on'], {
                "v": "2011-04-19"
            })

            self.assertDictEqual(as_secretary, as_resigned)

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
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(result['output_data']['metadata']['incorporation_date']['v'], '1957-01-01')
        self.assertTrue(len(result['output_data']['officers']['other']), 3)

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
        self.assertEqual(response.status_code, 200)
        result = response.json()
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
        self.assertEqual(response.status_code, 200)
        result = response.json()
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
        self.assertEqual(response.status_code, 200)
        result = response.json()
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
        self.assertEqual(response.status_code, 200)
        result = response.json()
        self.assertEqual(len(result['errors']), 0)
