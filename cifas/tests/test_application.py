import responses
from collections import namedtuple
from requests.exceptions import HTTPError, ConnectionError
from unittest import TestCase
from app.application import app
from tests import MATCH_RESPONSE, NOMATCH_RESPONSE, INDIVIDUAL_DATA_MINIMAL, \
    COMPANY_DATA_MINIMAL, MEMBERS_RESPONSE


class TestApplication(TestCase):
    def setUp(self):
        self.client = app.test_client()

    def run_cifas_search(self, input_data):
        return self.client.post(
            '/cifas-search',
            json={
                'config': {
                    'product_code': 'PXX',
                    'user_name': 'TestUser1234',
                    'member_id': 1232312312,
                    'use_uat': False,
                },
                'credentials': {
                    'cert': 'IAMAMACERTIFICATECHAIN',
                },
                'input_data': input_data,
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

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(INDIVIDUAL_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']
        matches = fraud_detection.get('matches')

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 1)
        self.assertEqual(len(matches), 1)
        self.assertEqual(matches[0]['reporting_company'], 'Member Practice')
        self.assertEqual(matches[0]['filing_reason'][0], 'Impersonation - previous address fraud')
        self.assertEqual(matches[0]['case_type'], 'Identity fraud')
        self.assertEqual(type(fraud_detection['search_reference']), str)

    @responses.activate
    def test_individual_nomatch(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=NOMATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(INDIVIDUAL_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 0)
        self.assertEqual(type(fraud_detection['search_reference']), str)

    @responses.activate
    def test_company_match(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(COMPANY_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 1)
        self.assertEqual(type(fraud_detection['search_reference']), str)

    @responses.activate
    def test_company_nomatch(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=NOMATCH_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(COMPANY_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']
        fraud_detection = output_data['fraud_detection']

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(errors), 0)
        self.assertEqual(fraud_detection['match_count'], 0)
        self.assertEqual(type(fraud_detection['search_reference']), str)

    @responses.activate
    def test_cifas_http_error(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=HTTPError(response=namedtuple('Response', ['text'])(
                text='Some HTTP error'
            )),
            content_type='text/xml; charset=utf-8',
        )

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(COMPANY_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(errors), 0)
        self.assertIsNone(output_data)

    @responses.activate
    def test_cifas_connection_error(self):
        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=ConnectionError(),
            content_type='text/xml; charset=utf-8',
        )

        responses.add(
            responses.POST,
            'https://services.find-cifas.org.uk/Direct/CIFAS/Request.asmx',
            body=MEMBERS_RESPONSE,
            content_type='text/xml; charset=utf-8',
        )

        response = self.run_cifas_search(COMPANY_DATA_MINIMAL)
        output_data = response.json['output_data']
        errors = response.json['errors']

        self.assertEqual(response.status_code, 200)
        self.assertGreater(len(errors), 0)
        self.assertIsNone(output_data)
