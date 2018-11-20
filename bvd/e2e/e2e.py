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
        tax_ids = [
            {'tax_id_type': 'EUROVAT', 'value': 'GB991242315'},
            {'tax_id_type': 'VAT', 'value': 'GB991242315'}
        ]
        self.assertCountEqual(metadata['tax_ids'], tax_ids)
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

    def test_success_registry_officer_bvd_id(self):
        response = requests.post(API_URL + '/registry-check', json={
            'input_data': {
                'country_of_incorporation': 'GBR',
                'number': '03977902',
            },
            'credentials': CREDENTIALS,
            'is_demo': False,
        })

        result = response.json()
        output_data = result['output_data']
        officers = output_data['officers']
        company_officers = [
            officer for role in ['directors', 'secretaries', 'resigned', 'others']
            for officer in officers[role]
            if officer['type'] == 'COMPANY'
        ]

        self.assertTrue(len(officers) > 0, 'missing company officers for this test!')

        for officer in company_officers:
            self.assertTrue(type(officer['bvd_id']) is str)

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
        self.assertEqual(metadata['tax_ids'], [])
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

    def test_success_demo_registry_check_with_tax_ids(self):
        response = requests.post(API_URL + '/registry-check', json={
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
        officers = output_data['officers']

        self.assertEqual(metadata['number'], '03875000')
        self.assertEqual(metadata['bvd_id'], 'GB03875000')
        self.assertEqual(metadata['incorporation_date'], '1999-11-11')
        self.assertEqual(metadata['company_type'], 'Private limited companies')
        tax_ids = [
            {'tax_id_type': 'EUROVAT', 'value': 'GB991242315'},
            {'tax_id_type': 'VAT', 'value': 'GB991242315'}
        ]
        self.assertCountEqual(metadata['tax_ids'], tax_ids)
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

    def test_success_demo_company_search(self):
        response = requests.post(API_URL + '/search', json={
            'input_data': {
                'country': 'GBR',
                'name': 'Passfort',
            },
            'credentials': CREDENTIALS,
            'is_demo': True,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()['output_data']

        self.assertEqual(len(result), 4)
        passfort_results = [x for x in result if x['number'] == '09565115']
        self.assertEqual(len(passfort_results), 1)
        self.assertEqual(passfort_results[0]['name'], 'PASSFORT LIMITED')
        self.assertEqual(passfort_results[0]['country'], 'GBR')
        self.assertEqual(passfort_results[0]['status'], 'Active')

    def test_failure_demo_company_search(self):
        response = requests.post(API_URL + '/search', json={
            'input_data': {
                'country': 'SAU',
                'name': 'Passfort',
            },
            'credentials': CREDENTIALS,
            'is_demo': True,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()['output_data']

        self.assertEqual(len(result), 4)

    def test_success_company_search(self):
        response = requests.post(API_URL + '/search', json={
            'input_data': {
                'country': 'GB',
                'name': 'Passfort',
            },
            'credentials': CREDENTIALS,
            'is_demo': False,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()['output_data']

        self.assertGreater(len(result), 0)
        passforts = [x for x in result if x['number'] == '09565115']
        self.assertEqual(len(passforts), 1)
        self.assertEqual(passforts[0]['name'], 'PASSFORT LIMITED')
        self.assertEqual(passforts[0]['country'], 'GBR')
        self.assertEqual(passforts[0]['status'], 'Active')

    def test_failure_company_search(self):
        response = requests.post(API_URL + '/search', json={
            'input_data': {
                'country': 'SAU',
                'name': 'QWERTYQWERTYQWERTY',
            },
            'credentials': CREDENTIALS,
            'is_demo': False,
        })

        self.assertEqual(response.status_code, 200)
        result = response.json()['output_data']

        self.assertEqual(len(result), 0)

    def test_error_company_search(self):
        response = requests.post(API_URL + '/search', json={
            'input_data': {
                'country': 'GBR',
                'name': 'Passfort',
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
