import responses
from unittest import TestCase
from app.application import app
from tests import MATCH_RESPONSE, NOMATCH_RESPONSE


class TestApplication(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def run_cifas_search(self):
        return self.client.post(
            '/cifas-search',
            json={
                'config': {
                    'product_code': 'PXX',
                    'search_type': 'XX',
                    'requesting_institution': 1232312312,
                    'use_uat': False,
                },
                'credentials': {
                    'cert': 'IAMAMACERTIFICATECHAIN',
                },
                'input_data': {
                    'entity_type': 'INDIVIDUAL',
                    'contact_details': {},
                    'personal_details': {
                        'dob': '1965-11-13',
                        'name': {
                            'family_name': 'Bridges',
                            'given_names': [
                                'Sam',
                                'Porter',
                            ]
                        }
                    },
                    'address_history': [
                        {
                            'address': {
                                'country': 'GBR',
                                'county': 'Tower Hamlets',
                                'locality': 'London',
                                'original_freeform_address': ', Passfort Ltd, 11, Princelet Street, London, , Tower Hamlets, , E1 6QH',
                                'original_structured_address': {
                                    'country': 'GBR',
                                    'county': 'Tower Hamlets',
                                    'locality': 'London',
                                    'postal_code': 'E1 6QH',
                                    'postal_town': '',
                                    'premise': 'Passfort Ltd',
                                    'route': 'Princelet Street',
                                    'state_province': '',
                                    'street_number': '11',
                                    'subpremise': ''
                                },
                                'postal_code': 'E1 6QH',
                                'postal_town': '',
                                'premise': 'Passfort Ltd',
                                'route': 'Princelet Street',
                                'state_province': '',
                                'street_number': '11',
                                'subpremise': '',
                                'type': 'STRUCTURED'
                            }
                        }
                    ]
                },
            },
        )

    @responses.activate
    def test_individual_match(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search()
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 1)
        self.assertEqual(type(fraud_detection['search_reference']), str)

    @responses.activate
    def test_individual_nomatch(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=NOMATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search()
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 0)
        self.assertEqual(type(fraud_detection['search_reference']), str)
