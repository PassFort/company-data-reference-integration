
import unittest
import requests


sandbox_token = 'test_bQqXUdkaKMHJczn9wxYcg6FiZoyiK8_A'
mock_request = {'config': {},
 'credentials': {'_cls': 'passfort_data_structure.stage_config.onfido.OnfidoCredentialsNoToken', 'token': sandbox_token},
 'input_data': {'_cls': 'python.models.entities.IndividualData.IndividualData',
                'address_history': {'all_': [[{'administrative_area_level_1': 'TX',
                                               'country': 'USA',
                                               'formatted_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                               'locality': 'Springfield',
                                               'original_address': ', 21, Fake '
                                                                   'street, '
                                                                   'Springfield, '
                                                                   'Springfield, '
                                                                   'TX, 42223',
                                               'original_structured_address': {'country': 'USA',
                                                                               'locality': 'Springfield',
                                                                               'postal_code': '42223',
                                                                               'postal_town': 'Springfield',
                                                                               'route': 'Fake '
                                                                                        'street',
                                                                               'state_province': 'TX',
                                                                               'street_number': '21',
                                                                               'subpremise': ''},
                                               'postal_code': '42223',
                                               'postal_town': 'Springfield',
                                               'route': 'Fake street',
                                               'street_number': '21',
                                               'subpremise': ''},
                                              {}]],
                                    'current': {'administrative_area_level_1': 'TX',
                                                'country': 'USA',
                                                'formatted_address': ', 21, '
                                                                     'Fake '
                                                                     'street, '
                                                                     'Springfield, '
                                                                     'Springfield, '
                                                                     'TX, '
                                                                     '42223',
                                                'locality': 'Springfield',
                                                'original_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                                'original_structured_address': {'country': 'USA',
                                                                                'locality': 'Springfield',
                                                                                'postal_code': '42223',
                                                                                'postal_town': 'Springfield',
                                                                                'route': 'Fake '
                                                                                         'street',
                                                                                'state_province': 'TX',
                                                                                'street_number': '21',
                                                                                'subpremise': ''},
                                                'postal_code': '42223',
                                                'postal_town': 'Springfield',
                                                'route': 'Fake street',
                                                'street_number': '21',
                                                'subpremise': ''}},
                'personal_details': {'dob': {'v': '1993-01-01'},
                                     'name': {'v': {'family_name': 'Persons',
                                                    'given_names': ['Name']}}}},
 'is_demo': False}


mock_failed_applicant_request = {
    **mock_request,
    'input_data':  {'_cls': 'python.models.entities.IndividualData.IndividualData',
                'address_history': {'all_': [[{'administrative_area_level_1': 'TX',
                                               'country': 'USA',
                                               'formatted_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                               'locality': 'Springfield',
                                               'original_address': ', 21, Fake '
                                                                   'street, '
                                                                   'Springfield, '
                                                                   'Springfield, '
                                                                   'TX, 42223',
                                               'original_structured_address': {'country': 'USA',
                                                                               'locality': 'Springfield',
                                                                               'postal_code': '42223',
                                                                               'postal_town': 'Springfield',
                                                                               'route': 'Fake '
                                                                                        'street',
                                                                               'state_province': 'TX',
                                                                               'street_number': '21',
                                                                               'subpremise': ''},
                                               'postal_code': '42223',
                                               'postal_town': 'Springfield',
                                               'route': 'Fake street',
                                               'street_number': '21',
                                               'subpremise': ''},
                                              {}]],
                                    'current': {'administrative_area_level_1': 'TX',
                                                'country': 'USA',
                                                'formatted_address': ', 21, '
                                                                     'Fake '
                                                                     'street, '
                                                                     'Springfield, '
                                                                     'Springfield, '
                                                                     'TX, '
                                                                     '42223',
                                                'locality': 'Springfield',
                                                'original_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                                'original_structured_address': {'country': 'USA',
                                                                                'locality': 'Springfield',
                                                                                'postal_code': '42223',
                                                                                'postal_town': 'Springfield',
                                                                                'route': 'Fake '
                                                                                         'street',
                                                                                'state_province': 'TX',
                                                                                'street_number': '21',
                                                                                'subpremise': ''},
                                                'postal_code': '42223',
                                                'postal_town': 'Springfield',
                                                'route': 'Fake street',
                                                'street_number': '21',
                                                'subpremise': ''}},
                'personal_details': {'dob': {'v': '2025-01-01'},
                                     'name': {'v': {'family_name': 'Person',
                                                    'given_names': ['PersonName']}}}},
}


url = 'http://127.0.0.1:8001/ekyc-check'
class EndToEndTests(unittest.TestCase):

    def test_success_correct_shape(self):
        response = requests.request('POST', url,
                                    json=mock_request
                                    )

        json_data = response.json()
        status = response.status_code
        self.assertEqual(200, status)

        self.assertIn('commercial_dob', json_data['output_data']['db_matches'])
        self.assertIn('credit_ref', json_data['output_data'])
        self.assertIn('check', json_data['raw'])
        self.assertIn('applicant', json_data['raw'])
        self.assertEqual(json_data['errors'], [])

    def test_failed_applicant(self):
        response = requests.request('POST', url,
                                    json=mock_failed_applicant_request,
                                    )

        json_data = response.json()
        status = response.status_code
        self.assertEqual(200, status)
        self.assertIn('applicant', json_data['raw'])
        self.assertIn("There was a validation error on this request", json_data['errors'][0]['error']['message'])
