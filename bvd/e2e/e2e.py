import unittest
import requests

API_URL = 'http://localhost:8001'

CREDENTIALS = {
    'key': '28RKd8ff3e08ca2be61194fa2c44fd99a5a0',
    'url': 'https://webservices.bvdep.com/rest/orbis/',
}

BAD_CREDENTIALS = {
    'key': '0a0a0a0a0a0a0a0a0a0a0a00a0a0a0a0a0a0a0a0',
    'url': 'https://webservices.bvdep.com/rest/orbis/',
}


class EndToEndTests(unittest.TestCase):

    def test_health_endpoint(self):
        response = requests.get(API_URL + '/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'success')

    def test_failed_registry_check(self):
        with self.subTest('invalid company number'):
            response = requests.post(API_URL + '/registry-check', json={
                'input_data': {
                    'country_of_incorporation': 'GBR',
                    'number': 'DMBDMBDMBDMB',
                },
                'credentials': CREDENTIALS,
                'is_demo': False,
            })

            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(len(result['errors']), 0)

    def test_error_registry_check(self):
        with self.subTest('invalid company number'):
            response = requests.post(API_URL + '/registry-check', json={
                'input_data': {
                    'country_of_incorporation': 'GBR',
                    'number': 'DMBDMBDMBDMB',
                },
                'credentials': BAD_CREDENTIALS,
                'is_demo': False,
            })

            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(len(result['errors']), 1)

            error = result['errors'][0]
            # Has connection_error error code
            self.assertEqual(error['code'], 302)
            self.assertEqual(error['source'], 'PROVIDER')
            self.assertEqual(error['info']['provider'], 'BvD')

    def test_success_registry_check(self):
        response = requests.post(API_URL + '/registry-check', json={
            'input_data': {
                'country_of_incorporation': 'GBR',
                'number': '03875000',
            },
            'credentials': CREDENTIALS,
            'is_demo': False,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()
        output_data = result['output_data']
        self.assertEqual(output_data['entity_type'], 'COMPANY')

        metadata = output_data['metadata']
        structured_company_type = metadata['structured_company_type']
        officers = output_data['officers']

        self.assertEqual(metadata['number'], '03875000')
        self.assertEqual(metadata['bvd_id'], 'GB03875000')
        self.assertEqual(metadata['incorporation_date'], '1999-11-11')
        self.assertEqual(metadata['company_type'], 'Private limited companies')
        self.assertEqual(structured_company_type['is_public'], False)
        self.assertEqual(structured_company_type['is_limited'], True)
        self.assertEqual(structured_company_type['ownership_type'], 'COMPANY')
        self.assertEqual(metadata['isin'], None)
        self.assertEqual(metadata['is_active'], True)
        self.assertIsInstance(metadata['freeform_address'], str)

        self.assertIsInstance(officers['directors'], list)
        self.assertIsInstance(officers['secretaries'], list)
        self.assertIsInstance(officers['resigned'], list)
        self.assertIsInstance(officers['others'], list)
        self.assertTrue(officers['directors'])

    def test_failed_ownership_check(self):
        with self.subTest('invalid company number'):
            response = requests.post(API_URL + '/ownership-check', json={
                'input_data': {
                    'country_of_incorporation': 'GBR',
                    'number': 'DMBDMBDMBDMB',
                },
                'credentials': CREDENTIALS,
                'is_demo': False,
            })

            self.assertEqual(response.status_code, 200)
            result = response.json()
            self.assertEqual(len(result['errors']), 0)

    def test_success_ownership_check(self):
        response = requests.post(API_URL + '/ownership-check', json={
            'input_data': {
                'country_of_incorporation': 'USA',
                'bvd_id': 'US912197729',
            },
            'credentials': CREDENTIALS,
            'is_demo': False,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()
        output_data = result['output_data']
        self.assertEqual(output_data['entity_type'], 'COMPANY')

        metadata = output_data['metadata']
        ownership = output_data['ownership_structure']
        structured_company_type = metadata['structured_company_type']

        self.assertTrue('beneficial_owners' in ownership.keys())
        self.assertTrue('shareholders' in ownership.keys())

        shareholders = ownership['shareholders']

        self.assertEqual(metadata['company_type'], 'Public limited companies')
        self.assertEqual(structured_company_type['is_public'], True)
        self.assertEqual(structured_company_type['is_limited'], True)
        self.assertEqual(structured_company_type['ownership_type'], 'COMPANY')

        self.assertTrue(len(shareholders) > 0)

    def test_success_demo_registry_check(self):
        response = requests.post(API_URL + '/registry-check', json={
            'input_data': {
                'country_of_incorporation': 'GBR',
                'number': '01493087',
            },
            'credentials': BAD_CREDENTIALS,
            'is_demo': True,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()
        output_data = result['output_data']
        self.assertEqual(output_data['entity_type'], 'COMPANY')

        metadata = output_data['metadata']
        structured_company_type = metadata['structured_company_type']
        officers = output_data['officers']

        self.assertEqual(metadata['number'], '01493087')
        self.assertEqual(metadata['bvd_id'], 'GB01493087')
        self.assertEqual(metadata['incorporation_date'], '1980-04-24')
        self.assertEqual(metadata['company_type'], 'Public limited companies')
        self.assertEqual(structured_company_type['is_public'], False)
        self.assertEqual(structured_company_type['is_limited'], True)
        self.assertEqual(structured_company_type['ownership_type'], 'COMPANY')
        self.assertEqual(metadata['isin'], None)
        self.assertEqual(metadata['is_active'], True)
        self.assertIsInstance(metadata['freeform_address'], str)

        self.assertIsInstance(officers['directors'], list)
        self.assertIsInstance(officers['secretaries'], list)
        self.assertIsInstance(officers['resigned'], list)
        self.assertIsInstance(officers['others'], list)
        self.assertTrue(officers['directors'])

    def test_success_demo_ownership_check(self):
        response = requests.post(API_URL + '/ownership-check', json={
            'input_data': {
                'country_of_incorporation': 'GBR',
                'bvd_id': 'GB03875000',
            },
            'credentials': BAD_CREDENTIALS,
            'is_demo': True,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()
        output_data = result['output_data']
        self.assertEqual(output_data['entity_type'], 'COMPANY')

        metadata = output_data['metadata']
        structured_company_type = metadata['structured_company_type']
        ownership = output_data['ownership_structure']

        self.assertTrue('beneficial_owners' in ownership.keys())
        self.assertTrue('shareholders' in ownership.keys())

        shareholders = ownership['shareholders']

        self.assertEqual(metadata['company_type'], 'Private limited companies')
        self.assertEqual(structured_company_type['is_public'], False)
        self.assertEqual(structured_company_type['is_limited'], True)
        self.assertEqual(structured_company_type['ownership_type'], 'COMPANY')

        self.assertTrue(len(shareholders) > 0)
