import requests
import unittest

API_URL = 'http://localhost:8001'

MOCK_PEIDS = ['873466', '2912358', '11847281', '4506663', '358285', '2984134']

class TestApiValidation(unittest.TestCase):

    def test_health_check_passes(self):
        response = requests.get(
            f'{API_URL}/health',
        )
        self.assertEqual(response.status_code, 200)

    def test_screening_returns_all_matches(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                'config': {
                    'ignore_deceased': False,
                    'include_adverse_media': True,
                    'include_adsr': True,
                    'include_associates': True,
                    'include_oel': True,
                    'include_ool': True,
                    'search_type': 'BROAD',
                    'strict_dob_search': True,
                },
                'credentials': {
                    'namespace': 'A_NAMESPACE',
                    'username': 'A_USERNAME',
                    'password': 'A_PASSWORD',
                    'url': 'A_URL',
                },
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['David', 'PEP'],
                            'family_name': 'Cameron'
                        },
                    }
                },
                'is_demo': True,
            }
        )
        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(len(body['errors']), 0)
        self.assertEqual(len(body['events']), len(MOCK_PEIDS))


class TestDemoChecks(unittest.TestCase):
    def test_pep_demo(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                'config': {
                    'ignore_deceased': False,
                    'include_adverse_media': True,
                    'include_adsr': True,
                    'include_associates': True,
                    'include_oel': True,
                    'include_ool': True,
                    'search_type': 'BROAD',
                    'strict_dob_search': True,
                },
                'credentials': {
                    'namespace': 'A_NAMESPACE',
                    'username': 'A_USERNAME',
                    'password': 'A_PASSWORD',
                    'url': 'A_URL',
                },
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['David', 'PEP'],
                            'family_name': 'Cameron'
                        },
                    }
                },
                'is_demo': True,
            }
        )
        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(len(body['errors']), 0)
        self.assertTrue(any(event['event_type'] == 'PEP_FLAG' for event in body['events']))


    def test_limit_fail(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                'config': {
                    'ignore_deceased': False,
                    'include_adverse_media': True,
                    'include_adsr': True,
                    'include_associates': True,
                    'include_oel': True,
                    'include_ool': True,
                    'search_type': 'BROAD',
                    'strict_dob_search': True,
                },
                'credentials': {
                    'namespace': 'A_NAMESPACE',
                    'username': 'A_USERNAME',
                    'password': 'A_PASSWORD',
                    'url': 'A_URL',
                },
                'limit': 3,
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['David', 'PEP'],
                            'family_name': 'Cameron'
                        },
                    }
                },
                'is_demo': True,
            }
        )
        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(len(body['errors']), 1)
        self.assertEqual(body['errors'][0], {
            "code": 108,
            "info": {
                "count": 6,
                "limit": 3
            },
            "message": "The check has returned 6 matches. A maximum of 3 matches can be processed. Please log into your provider portal to see the matches. Contact us to see if it's possible to increase the match strength to reduce the number of matches.",
            "source": "ENGINE",
        })

    def test_sanctions_demo(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                'config': {
                    'ignore_deceased': False,
                    'include_adverse_media': True,
                    'include_adsr': True,
                    'include_associates': True,
                    'include_oel': True,
                    'include_ool': True,
                    'search_type': 'BROAD',
                    'strict_dob_search': True,
                },
                'credentials': {
                    'namespace': 'A_NAMESPACE',
                    'username': 'A_USERNAME',
                    'password': 'A_PASSWORD',
                    'url': 'A_URL',
                },
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['Bashar', 'sanction'],
                            'family_name': 'Assad'
                        },
                    }
                },
                'is_demo': True,
            }
        )
        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(len(body['errors']), 0)
        self.assertTrue(any(event['event_type'] == 'SANCTION_FLAG' for event in body['events']))

    def test_media_demo(self):
        response = requests.post(
            f'{API_URL}/screening_request',
            json={
                'config': {
                    'ignore_deceased': False,
                    'include_adverse_media': True,
                    'include_adsr': True,
                    'include_associates': True,
                    'include_oel': True,
                    'include_ool': True,
                    'search_type': 'BROAD',
                    'strict_dob_search': True,
                },
                'credentials': {
                    'namespace': 'A_NAMESPACE',
                    'username': 'A_USERNAME',
                    'password': 'A_PASSWORD',
                    'url': 'A_URL',
                },
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['Hugo', 'media'],
                            'family_name': 'Chavez'
                        },
                    }
                },
                'is_demo': True,
            }
        )
        self.assertEqual(response.status_code, 200)

        body = response.json()

        self.assertEqual(len(body['errors']), 0)
        self.assertTrue(any(event['event_type'] == 'ADVERSE_MEDIA_FLAG' for event in body['events']))
