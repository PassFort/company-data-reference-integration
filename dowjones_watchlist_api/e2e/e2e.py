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
                            'given_names': ['A_FIRST_NAME', 'A_MIDDLE_NAME'],
                            'family_name': 'A_SECOND_NAME'
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
