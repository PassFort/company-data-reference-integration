"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response from the provider
"""

import responses
import unittest


from .application import app
from .api.types import ErrorCode


TEST_SEARCH_REQUEST = {
    'credentials': {
        'username': 'x',
        'password': 'y'
    },
    'input_data': {
        'query': 'test',
        'country': 'GBR'
    }
}


TEST_REPORT_REQUEST = {
    'credentials': {
        'username': 'x',
        'password': 'y'
    },
    'input_data': {
        'creditsafe_id': 'testID'
    }
}


SEARCH_RESPONSE = {
    "totalSize": 1,
    "companies": [
        {
            "id": "GB001-0-09565115",
            "country": "GB",
            "regNo": "09565115",
            "safeNo": "UK13646576",
            "name": "PASSFORT LIMITED",
            "address": {
                "simpleValue": "11 PRINCELET STREET, LONDON, Greater London, E1 6QH",
                "city": "LONDON",
                "postCode": "E1 6QH"
            },
            "status": "Active",
            "type": "Ltd",
            "dateOfLatestAccounts": "2017-12-31T00:00:00.000000Z",
            "dateOfLatestChange": "2019-07-03T01:27:52.000Z",
            "activityCode": "7222",
            "statusDescription": "Active - Accounts Filed"
        }
    ]
}


class TestHandleSearchRequestErrors(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_bad_key_returns_configuration_error(self):
        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'][0]['code'], ErrorCode.MISCONFIGURATION_ERROR.value)

    @responses.activate
    def test_provider_unreachable_returns_connection_error(self):
        # Not setting a response will make the unreachable
        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST)
        self.assertEqual(result.status_code, 502)
        self.assertEqual(result.json['errors'][0]['code'], ErrorCode.PROVIDER_CONNECTION_ERROR.value)

    @responses.activate
    def test_no_company_found(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?name=test&countries=GB&pageSize=100',
            json={'companies': []},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?regNo=test&countries=GB&pageSize=100',
            json={'companies': []},
            status=200)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'], [])
        self.assertEqual(result.json['output_data'], [])

    @responses.activate
    def test_ignores_errors_when_there_is_at_least_one_result(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?name=test&countries=GB&pageSize=100',
            json=SEARCH_RESPONSE,
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?regNo=test&countries=GB&pageSize=100',
            json={'details': 'Param not supported'},
            status=400)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(
            result.json['output_data'],
            [
                {
                    'name': 'PASSFORT LIMITED',
                    'number': '09565115',
                    'creditsafe_id': 'GB001-0-09565115',
                    'country_of_incorporation': 'GBR'
                }
            ]
        )

    @responses.activate
    def test_search_returns_errors_from_provider_if_no_results(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?name=test&countries=GB&pageSize=100',
            json={'details': 'Param not supported'},
            status=400)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'][0]['message'],
                         'Unable to perform a search using the parameters provided')


class TestReport(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    @responses.activate
    def test_bad_id(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies/testID',
            json={
                "messages": [
                    {
                        "code": "ReportUnavailable",
                        "text": "Report unavailable.",
                        "type": "Information"
                    }
                ],
                "correlationId": "1a703860-ca4f-11e9-9c9d-02562b862d16"
            },
            status=400)
        result = self.app.post(
            '/company_report',
            json=TEST_REPORT_REQUEST
        )

        self.assertEqual(result.status_code, 400)
        self.assertEqual(result.json['errors'][0]['message'],
                         'Bad ID provided')

    @responses.activate
    def test_no_access_to_reports(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies/testID',
            json={
                "details": "No access to RO reports",
                "correlationId": "23028240-ca67-11e9-b779-06ca8693e6f8",
                "message": "Forbidden request"
            },
            status=403)

        result = self.app.post(
            '/company_report',
            json=TEST_REPORT_REQUEST
        )
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'][0]['message'],
                         'The request could not be authorised')
        self.assertEqual(result.json['errors'][0]['info']['provider_error']['message'],
                         'No access to RO reports')


class TestDemoData(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_pass(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': 'test',
                    'country': 'GBR'
                }
            }
        ).json
        with self.subTest('returns demo company data, with pass id'):
            self.assertEqual(len(search_response['output_data']), 1)
            self.assertDictEqual(
                search_response['output_data'][0],
                {
                    'name': 'PASSFORT LIMITED',
                    'number': '09565115',
                    'creditsafe_id': 'pass',
                    'country_of_incorporation': 'GBR'
                }
            )

        report_response = self.app.post(
            '/company_report',
            json={
                'is_demo': True,
                'input_data': {
                    'creditsafe_id': 'pass',
                }
            }
        ).json

        with self.subTest('returns demo company report, with pass id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '09565115')

    def test_partial(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': ' gfr partial grgeger$',
                    'country': 'GBR'
                }
            }
        ).json
        with self.subTest('returns demo company data, with partial id'):
            self.assertEqual(len(search_response['output_data']), 1)
            self.assertDictEqual(
                search_response['output_data'][0],
                {
                    'name': 'PASSFORT LIMITED',
                    'number': '09565115',
                    'creditsafe_id': 'partial',
                    'country_of_incorporation': 'GBR'
                }
            )

        report_response = self.app.post(
            '/company_report',
            json={
                'is_demo': True,
                'input_data': {
                    'creditsafe_id': 'partial',
                }
            }
        ).json

        with self.subTest('returns demo company report, with partial id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '1111111')

    def test_fail(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': ' gfr fail grgeger$',
                    'country': 'GBR'
                }
            }
        ).json
        self.assertEqual(len(search_response['output_data']), 0)
