"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response from the provider
"""

import responses
import unittest
import uuid
import math
import json
from unittest import mock
from datetime import datetime, timedelta
from itertools import chain
from random import randint

from .application import app
from .api.types import ErrorCode
from .api.event_mappings import get_configure_event_payload, MonitoringConfigType


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


TEST_PORTFOLIO_REQUEST = {
    'credentials': {
        'username': 'x',
        'password': 'y'
    },
    'portfolio_name': 'Test portfolio name'
}


TEST_MONITORING_REQUEST = {
    'credentials': {
        'username': 'x',
        'password': 'y'
    },
    'portfolio_id': 111111111,
    'creditsafe_id': 'testID'
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

MOCK_COMPANY = {
    "portfolioId": 1111111,
    "safeNumber": "FR123456789",
    "countryCode": "FR",
    "name": "A Company",
    "address": "24 Leftside, Paris, 23456",
    "personalReference": "Some text",
    "companyStatus": "Active",
    "creditLimit": 10000,
    "ratingLocal": 76,
    "ratingCommon": "B",
    "dateLastEvent": "2017-04-18T15:00:00.050Z",
    "id": "FR01-000-584758989"
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
        self.assertEqual(result.status_code, 200)
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
            'https://connect.creditsafe.com/v1/companies?regNo=test&countries=GB&exact=True&pageSize=100',
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
            'https://connect.creditsafe.com/v1/companies?regNo=test&countries=GB&exact=True&pageSize=100',
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
            json={'details': 'Parameters not supported'},
            status=400)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )

        self.assertEqual(result.status_code, 200)
        self.assertIn('Parameters not supported', result.json['errors'][0]['message'])

    @responses.activate
    def test_search_returns_invalid_input_from_creditsafe(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?name=test&countries=GB&pageSize=100',
            json={'details': 'shorter than the required minimum lenght of'},
            status=400)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'][0]['code'], 201)  # invalid input

    @responses.activate
    def test_search_returns_unsupported_country(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/companies?name=test&countries=GB&pageSize=100',
            json={'details': 'ZA is not a supported country'},
            status=400)

        result = self.app.post(
            '/search',
            json=TEST_SEARCH_REQUEST
        )
        print(result)
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json['errors'][0]['code'], 106)
        self.assertEqual(
            result.json['errors'][0]['message'],
            "Country 'South Africa' is not supported by the provider"
        )


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

        self.assertEqual(result.status_code, 200)
        self.assertIn('The provider returned an error when running this check: ', result.json['errors'][0]['message'])

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
        self.assertIn('The request could not be authorised', result.json['errors'][0]['message'])
        self.assertIn('No access to RO reports', result.json['errors'][0]['message'])


class TestDemoData(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    def test_pass_uk(self):
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
                    'country_of_incorporation': 'GBR'
                }
            }
        ).json

        with self.subTest('returns demo company report, with pass id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '09565115')

        with self.subTest('returns associates'):
            self.assertEqual(len(report_response['output_data']['associated_entities']), 29)

    def test_partial_uk(self):
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
                    'name': 'PASSFORT PARTIAL LIMITED',
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
                    'country_of_incorporation': 'GBR'
                }
            }
        ).json

        with self.subTest('returns demo company report, with partial id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '1111111')

    def test_pass_global(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': 'test',
                    'country': 'FRA'
                }
            }
        ).json
        with self.subTest('returns demo company data, with pass id'):
            self.assertEqual(len(search_response['output_data']), 1)
            self.assertDictEqual(
                search_response['output_data'][0],
                {
                    'name': 'Aerial Traders',
                    'number': '5560642554',
                    'creditsafe_id': 'pass',
                    'country_of_incorporation': 'FRA'
                }
            )

        report_response = self.app.post(
            '/company_report',
            json={
                'is_demo': True,
                'input_data': {
                    'creditsafe_id': 'pass',
                    'country_of_incorporation': 'FRA'
                }
            }
        ).json

        with self.subTest('returns demo company report, with pass id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '5560642554')
            self.assertEqual(report_response['output_data']['metadata']['name'], 'Aerial Traders')

    def test_partial_global(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': ' gfr partial grgeger$',
                    'country': 'FRA'
                }
            }
        ).json
        with self.subTest('returns demo company data, with partial id'):
            self.assertEqual(len(search_response['output_data']), 1)
            self.assertDictEqual(
                search_response['output_data'][0],
                {
                    'name': 'Aerial Traders PARTIAL',
                    'number': '5560642554',
                    'creditsafe_id': 'partial',
                    'country_of_incorporation': 'FRA'
                }
            )

        report_response = self.app.post(
            '/company_report',
            json={
                'is_demo': True,
                'input_data': {
                    'creditsafe_id': 'partial',
                    'country_of_incorporation': 'FRA'
                }
            }
        ).json

        with self.subTest('returns demo company report, with partial id'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '1111111')
            self.assertEqual(report_response['output_data']['metadata']['name'], 'Aerial Traders PARTIAL')

    def test_partial_financials_global(self):
        search_response = self.app.post(
            '/search',
            json={
                'is_demo': True,
                'input_data': {
                    'query': ' gfr partial_financial grgeger$',
                    'country': 'FRA'
                }
            }
        ).json
        with self.subTest('returns demo company data, with partial id'):
            self.assertEqual(len(search_response['output_data']), 1)
            self.assertDictEqual(
                search_response['output_data'][0],
                {
                    'name': 'Aerial Traders PARTIAL FINANCIAL',
                    'number': '5560642554',
                    'creditsafe_id': 'partial_financial',
                    'country_of_incorporation': 'FRA'
                }
            )

        report_response = self.app.post(
            '/company_report',
            json={
                'is_demo': True,
                'input_data': {
                    'creditsafe_id': 'partial_financial',
                    'country_of_incorporation': 'FRA'
                }
            }
        ).json

        with self.subTest('returns demo company report, with no statements'):
            self.assertEqual(report_response['output_data']['metadata']['number'], '5560642554')
            self.assertEqual(report_response['output_data']['metadata']['name'], 'Aerial Traders PARTIAL FINANCIAL')
            self.assertEqual(report_response['output_data']['financials'], None)

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


class TestMonitoring(unittest.TestCase):

    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True
        self.configure_event_payload = get_configure_event_payload()
        self.mock_authentication()

    def mock_authentication(self):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

    def mock_creditsafe_portfolio_response(self, status, json):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/monitoring/portfolios',
            json=json,
            status=status)

    def mock_creditsafe_get_company_response(self, status, json):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/portfolios/111111111/companies/testID',
            json=json,
            status=status)

    def mock_creditsafe_monitoring_response(self, status, json):
        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/monitoring/portfolios/111111111/companies',
            json=json,
            status=status)

    def mock_creditsafe_configure_events_response(self, status, json):
        for country_code in self.configure_event_payload:
            responses.add(
                responses.PUT,
                f'https://connect.creditsafe.com/v1/monitoring/portfolios/12345678/eventRules/{country_code}',
                json=json,
                status=status
            )

    @responses.activate
    def test_create_portfolio(self):
        self.mock_creditsafe_portfolio_response(200, {
            'portfolioId': 12345678,
            'name': 'Test portfolio name',
            'isDefault': False
        })
        self.mock_creditsafe_configure_events_response(204, {})

        portfolio_response = self.app.post(
            '/monitoring_portfolio',
            json=TEST_PORTFOLIO_REQUEST
        )
        self.assertEqual(portfolio_response.status_code, 200)
        self.assertEqual(portfolio_response.json['portfolio_id'], 12345678)

        # 1 get token call + 1 create portfolio call + 1 call to configure events per supported country
        self.assertEqual(len(responses.calls), 2 + len(self.configure_event_payload))

    @responses.activate
    def test_create_portfolio_bad_request(self):
        self.mock_creditsafe_portfolio_response(400, {
            'message': 'Bad request'
        })

        portfolio_response = self.app.post(
            '/monitoring_portfolio',
            json=TEST_PORTFOLIO_REQUEST
        )

        self.assertEqual(portfolio_response.status_code, 200)
        self.assertIn('Bad request', portfolio_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_portfolio_access_forbidden(self):
        self.mock_creditsafe_portfolio_response(403, {
            'message': 'Access forbidden'
        })

        portfolio_response = self.app.post(
            '/monitoring_portfolio',
            json=TEST_PORTFOLIO_REQUEST
        )

        self.assertEqual(portfolio_response.status_code, 200)
        self.assertIn('The request could not be authorised: Access forbidden', portfolio_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_portfolio_not_found(self):
        self.mock_creditsafe_portfolio_response(404, {
            'message': 'Not found'
        })

        portfolio_response = self.app.post(
            '/monitoring_portfolio',
            json=TEST_PORTFOLIO_REQUEST
        )
        self.assertEqual(portfolio_response.status_code, 200)
        self.assertIn('Not found', portfolio_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_portfolio_unhandled_error(self):
        self.mock_creditsafe_portfolio_response(500, {
            'message': 'Unhandled error'
        })

        portfolio_response = self.app.post(
            '/monitoring_portfolio',
            json=TEST_PORTFOLIO_REQUEST
        )

        self.assertEqual(portfolio_response.status_code, 200)
        self.assertIn(
            "The provider returned an error when running this check: 'Unhandled error' while running 'Creditsafe' service. Please get in touch for more information",
            portfolio_response.json['errors'][0]['message']
        )

    @responses.activate
    def test_enable_monitoring_existing_company(self):
        self.mock_creditsafe_get_company_response(200, MOCK_COMPANY)

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)

    @responses.activate
    def test_enable_monitoring(self):
        self.mock_creditsafe_get_company_response(400, {'message': 'PortfolioCompany not found'})
        self.mock_creditsafe_monitoring_response(201, {
            'message': 'Company added'
        })

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)

    @responses.activate
    def test_get_company_unhandled_error(self):
        self.mock_creditsafe_get_company_response(500, {'message': 'Unhandled error'})

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn("The provider returned an error when running this check: 'Unhandled error' while running 'Creditsafe' service. Please get in touch for more information",
            monitoring_response.json['errors'][0]['message'])

    @responses.activate
    def test_enabled_monitoring_unhandled_error(self):
        self.mock_creditsafe_get_company_response(404, {'message': 'Company resource not found'})
        self.mock_creditsafe_monitoring_response(500, {
            'message': 'Unhandled error'
        })

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn(
            "The provider returned an error when running this check: 'Unhandled error' while running 'Creditsafe' service. Please get in touch for more information",
            monitoring_response.json['errors'][0]['message']
        )

    @responses.activate
    def test_get_company_bad_request(self):
        self.mock_creditsafe_get_company_response(400, {'message': 'Bad request'})

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn('Bad request', monitoring_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_monitoring_bad_request(self):
        self.mock_creditsafe_get_company_response(404, {'message': 'Company resource not found'})
        self.mock_creditsafe_monitoring_response(400, {
            'message': 'Bad request'
        })

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )

        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn('Bad request', monitoring_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_monitoring_access_forbidden(self):
        self.mock_creditsafe_get_company_response(403, {
            'message': 'Access forbidden'
        })

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )
        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn('The request could not be authorised: Access forbidden', monitoring_response.json['errors'][0]['message'])

    @responses.activate
    def test_create_monitoring_not_found(self):
        self.mock_creditsafe_get_company_response(404, {'message': 'Company resource not found'})
        self.mock_creditsafe_monitoring_response(404, {
            'message': 'Not found'
        })

        monitoring_response = self.app.post(
            '/monitoring',
            json=TEST_MONITORING_REQUEST
        )
        self.assertEqual(monitoring_response.status_code, 200)
        self.assertIn('Not found', monitoring_response.json['errors'][0]['message'])


class TestGetMonitoringEvents(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

        self.date_regex = r'\d{4}-\d{2}-\d{2}T\d{2}:\d{2}:\d{2}.*'
        crt_time = datetime.now()
        self.test_start_date = crt_time - timedelta(days=2)
        self.test_end_date = crt_time - timedelta(days=1)

        responses.add(
            responses.POST,
            'https://connect.creditsafe.com/v1/authenticate',
            json={'token': 'test'},
            status=200)

    def get_mock_request(self, monitoring_configs=None):
        if not monitoring_configs:
            monitoring_configs = [{
                'institution_config_id': uuid.uuid4(),
                'portfolio_id': 111111111,
                'last_run_date': self.test_start_date.isoformat()
            }]

        return {
            'credentials': {
                'username': 'x',
                'password': 'y'
            },
            'monitoring_configs': monitoring_configs,
            'callback_url': 'http://flask:9090/creditsafe/ongoing_monitoring'
        }

    def mock_creditsafe_monitoring_pagination_events_response(self, num_events):
        num_of_pages = math.ceil(num_events / 1000)
        rule_code_choices = [101, 105, 107]
        for page_num in range(num_of_pages):
            res = {
                "totalCount": num_events,
                "data": [
                    {
                        "company": {
                            "id": "US-X-US22384484",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 589960,
                            "portfolioName": "Default"
                        },
                        "eventId": randint(1, 9999999999),
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": rule_code_choices[idx % 3],
                        "ruleName": "Address"
                    }
                    for idx in range(
                        # Generate 1000 events except for the last page
                        (1000 if page_num + 1 < num_of_pages else num_events % 1000)
                    )
                ],
                "paging": {
                    "size": 1000,
                    "prev": page_num - 1 if page_num > 0 else None,
                    "next": page_num + 1 if page_num + 1 < num_of_pages else None,
                    "last": num_of_pages
                }
            }
            responses.add(
                responses.GET,
                'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
                json=res,
                status=200
            )

    def mock_creditsafe_monitoring_events_response(self, status, json):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json=json,
            status=status
        )

    def get_mock_callback_arguments(self, callback_mock):
        args, kwargs = callback_mock.call_args_list[0]
        return args[0], args[1], args[2], args[3]

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_no_data(self, callback_mock):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={
                'totalCount': 0,
                'data': [],
                'paging': {
                    'size': 1000,
                    'prev': None,
                    'next': None,
                    'last': -1
                }
            },
            status=200
        )

        institution_config_id = uuid.uuid4()
        configs = [{
            'institution_config_id': institution_config_id,
            'portfolio_id': 123454321,
            'last_run_date': self.test_start_date.isoformat()
        }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(len(responses.calls), 2)
        self.assertEqual(responses.calls[0].request.url, 'https://connect.creditsafe.com/v1/authenticate')
        self.assertIn('https://connect.creditsafe.com/v1/monitoring/notificationEvents', responses.calls[1].request.url)

        self.assertEqual(callback_mock.call_count, 1)
        callback_url, config, events, raw_events = self.get_mock_callback_arguments(callback_mock)

        self.assertEqual(callback_url, 'http://flask:9090/creditsafe/ongoing_monitoring')
        self.assertEqual(config.institution_config_id, institution_config_id)
        self.assertEqual(config.portfolio_id, 123454321)

        self.assertEqual(len(events), 0)
        # Number of processed events should be the same length as raw_data
        self.assertEqual(len(events), len(raw_events))

        self.assertEqual(monitoring_events_response.status_code, 200)

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_single_page_data(self, callback_mock):
        self.mock_creditsafe_monitoring_pagination_events_response(10)

        institution_config_id = uuid.uuid4()
        configs = [{
            'institution_config_id': institution_config_id,
            'portfolio_id': 589960,
            'last_run_date': self.test_start_date.isoformat()
        }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)

        self.assertEqual(callback_mock.call_count, 1)
        callback_url, config, events, raw_events = self.get_mock_callback_arguments(callback_mock)

        self.assertEqual(callback_url, 'http://flask:9090/creditsafe/ongoing_monitoring')
        self.assertEqual(config.institution_config_id, institution_config_id)
        self.assertEqual(config.portfolio_id, 589960)

        self.assertEqual(len(events), 10)
        # Number of processed events should be the same length as raw_data
        self.assertEqual(len(events), len(raw_events))

        for raw_event in raw_events:
            for expected_property in ['company', 'eventId', 'eventDate', 'notificationEventId', 'ruleCode', 'ruleName']:
                self.assertIn(expected_property, raw_event)

        expected_config_types = [config.value for config in MonitoringConfigType]
        expected_rule_codes = [101, 105, 107]

        for event in events:
            self.assertIn(event['event_type'], expected_config_types)
            self.assertRegex(event['event_date'], self.date_regex)
            self.assertIn(event['rule_code'], expected_rule_codes)

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_multi_page_data(self, callback_mock):
        self.mock_creditsafe_monitoring_pagination_events_response(3001)

        institution_config_id = uuid.uuid4()
        configs = [{
            'institution_config_id': institution_config_id,
            'portfolio_id': 589960,
            'last_run_date': self.test_start_date.isoformat()
        }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)

        self.assertEqual(callback_mock.call_count, 1)
        callback_url, config, events, raw_events = self.get_mock_callback_arguments(callback_mock)

        self.assertEqual(callback_url, 'http://flask:9090/creditsafe/ongoing_monitoring')
        self.assertEqual(len(events), 3001)
        # Number of processed events should be the same length as raw_data
        self.assertEqual(len(events), len(raw_events))

        # Raw event should have all properties as those coming directly from the Creditsafe API
        for raw_event in raw_events:
            for expected_property in ['company', 'eventId', 'eventDate', 'notificationEventId', 'ruleCode', 'ruleName']:
                self.assertIn(expected_property, raw_event)

        expected_config_types = [config.value for config in MonitoringConfigType]
        expected_rule_codes = [101, 105, 107]

        for event in events:
            self.assertIn(event['event_type'], expected_config_types)
            self.assertRegex(event['event_date'], self.date_regex)
            self.assertIn(event['rule_code'], expected_rule_codes)

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_multiple_events_search(self, callback_mock):
        """Checks that one request is sent per MonitoringEventsSearch instance when their last_run_dates
        are not the same."""

        self.mock_creditsafe_monitoring_pagination_events_response(10)

        configs = [{
            'institution_config_id': uuid.uuid4(),
            'portfolio_id': 11111111,
            'last_run_date': self.test_start_date.isoformat()
        }, {
            'institution_config_id': uuid.uuid4(),
            'portfolio_id': 22222222,
            'last_run_date': (self.test_start_date + timedelta(seconds=1)).isoformat()
        }, {
            'institution_config_id': uuid.uuid4(),
            'portfolio_id': 33333333,
            'last_run_date': (self.test_start_date + timedelta(seconds=2)).isoformat()
        }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertEqual(len(responses.calls), 4)  # 1 get token call + 3 expected get events calls

        self.assertEqual(callback_mock.call_count, 3)

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_multiple_events_search_same_last_run_date(self, callback_mock):
        """Checks that only one request is sent even when the last_run_date is the same across all
        MonitoringEventsSearch instances."""

        self.mock_creditsafe_monitoring_pagination_events_response(10)
        last_run_date = self.test_start_date.isoformat()
        configs = [{
            'portfolio_id': 111111111,
            'institution_config_id': uuid.uuid4(),
            'last_run_date': last_run_date
        } for _ in range(5)]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertEqual(len(responses.calls), 2)  # 1 get token call + 1 expected get events call

        self.assertEqual(callback_mock.call_count, 5)

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_unknown_creditsafe_events(self, callback_mock):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={
                "totalCount": 1,
                "data": [
                    {
                        "company": {
                            "id": "US-X-US22384484",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 589960,
                            "portfolioName": "Default"
                        },
                        "eventId": 12345678,
                        "eventDate": self.test_end_date.isoformat(),
                        "notificationEventId": 12345678,
                        "ruleCode": 9001,  # Rule code doesn't exist in the mapping
                        "ruleName": "Unknown rule"
                    }
                ],
                "paging": {
                    "size": 1000,
                    "prev": None,
                    "next": None,
                    "last": 0
                }
            },
            status=200
        )

        institution_config_id = uuid.uuid4()
        configs = [{
            'institution_config_id': institution_config_id,
            'portfolio_id': 12321,
            'last_run_date': self.test_start_date.isoformat()
        }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(callback_mock.call_count, 1)
        callback_url, config, events, raw_events = self.get_mock_callback_arguments(callback_mock)

        self.assertEqual(callback_url, 'http://flask:9090/creditsafe/ongoing_monitoring')
        self.assertEqual(config.institution_config_id, institution_config_id)
        self.assertEqual(config.portfolio_id, 12321)

        self.assertEqual(len(events), 0)
        # Number of processed events should be the same length as raw_data
        self.assertEqual(len(events), len(raw_events))
        self.assertEqual(monitoring_events_response.status_code, 200)

    @responses.activate
    def test_multiple_portfolios(self):
        """
        Checks when we have multiple configs/portfolios with the same start date, the events
        endpoint is called once, and the callback is called once per config.
        """
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={
                "totalCount": 3,
                "data": [
                    {
                        "company": {
                            "id": "UK-11111111",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 11111111, # portfolio ID for first config
                            "portfolioName": "Default"
                        },
                        "eventId": 101010101,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 101,
                        "ruleName": "Address"
                    },
                    {
                        "company": {
                            "id": "UK-2222222",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 22222222, # portfolio ID for second config
                            "portfolioName": "Default"
                        },
                        "eventId": 202020202,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 105,
                        "ruleName": "Address"
                    },
                    {
                        "company": {
                            "id": "UK-33333333",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 33333333, # unknown portfolio ID
                            "portfolioName": "Default"
                        },
                        "eventId": 3030303,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 107,
                        "ruleName": "Address"
                    }

                ],
                "paging": {
                    "size": 1000,
                    "prev": None,
                    "next": None,
                    "last": 0
                }
            },
            status=200
        )

        institution_config_id = uuid.uuid4()
        institution_config_id_2 = uuid.uuid4()
        last_run_date = self.test_start_date.isoformat()
        configs = [{
            'institution_config_id': str(institution_config_id),
            'portfolio_id': 11111111,
            'last_run_date': last_run_date
        }, {
            'institution_config_id': str(institution_config_id_2),
            'portfolio_id': 22222222,
            'last_run_date': last_run_date
        }]

        responses.add(
            responses.POST,
            'http://flask:9090/creditsafe/ongoing_monitoring',
            status=200)

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)

        # the first call is to the authenticate endpoint, and the second is to the get events endpoint
        self.assertEqual(len(responses.calls), 4)

        # the last two calls are to the monolith callback
        first_callback = json.loads(responses.calls[2].request.body.decode('utf-8'))

        self.assertEqual(first_callback['institution_config_id'], str(institution_config_id))
        self.assertEqual(first_callback['portfolio_id'], 11111111)
        self.assertIsNotNone(first_callback['last_run_date'])
        self.assertEqual(len(first_callback['events']), 1)
        self.assertEqual(first_callback['events'][0]['creditsafe_id'], 'UK-11111111')
        self.assertEqual(len(first_callback['raw_data']), 1)

        second_callback = json.loads(responses.calls[3].request.body.decode('utf-8'))

        self.assertEqual(second_callback['institution_config_id'], str(institution_config_id_2))
        self.assertEqual(second_callback['portfolio_id'], 22222222)
        self.assertIsNotNone(second_callback['last_run_date'])
        self.assertEqual(len(second_callback['events']), 1)
        self.assertEqual(second_callback['events'][0]['creditsafe_id'], 'UK-2222222')
        self.assertEqual(len(second_callback['raw_data']), 1)


    @responses.activate
    def test_multiple_portfolios_different_last_run_date(self):
        """
        Checks when we have different start dates across multiple portfolios, it calls the
        events endpoint twice, and the callback only once per config
        """
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={
                "totalCount": 3,
                "data": [
                    {
                        "company": {
                            "id": "UK-11111111",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 11111111, # portfolio ID for first config
                            "portfolioName": "Default"
                        },
                        "eventId": 101010101,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 101,
                        "ruleName": "Address"
                    },
                    {
                        "company": {
                            "id": "UK-2222222",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 22222222, # portfolio ID for second config
                            "portfolioName": "Default"
                        },
                        "eventId": 202020202,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 105,
                        "ruleName": "Address"
                    },
                    {
                        "company": {
                            "id": "UK-33333333",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 33333333, # unknown portfolio ID
                            "portfolioName": "Default"
                        },
                        "eventId": 3030303,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 107,
                        "ruleName": "Address"
                    }

                ],
                "paging": {
                    "size": 1000,
                    "prev": None,
                    "next": None,
                    "last": 0
                }
            },
            status=200
        )

        institution_config_id = uuid.uuid4()
        institution_config_id_2 = uuid.uuid4()
        configs = [{
            'institution_config_id': str(institution_config_id),
            'portfolio_id': 11111111,
            'last_run_date': self.test_start_date.isoformat()
        }, {
            'institution_config_id': str(institution_config_id_2),
            'portfolio_id': 22222222,
            'last_run_date': (self.test_start_date + timedelta(seconds=10)).isoformat()
        }]

        responses.add(
            responses.POST,
            'http://flask:9090/creditsafe/ongoing_monitoring',
            status=200)

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        self.assertEqual(monitoring_events_response.status_code, 200)

        # the first call is to the authenticate endpoint, and the second and third are to the get events endpoint
        self.assertEqual(len(responses.calls), 5)

        # the last two calls are to the monolith callback
        first_callback = json.loads(responses.calls[3].request.body.decode('utf-8'))

        self.assertEqual(first_callback['institution_config_id'], str(institution_config_id))
        self.assertEqual(first_callback['portfolio_id'], 11111111)
        self.assertIsNotNone(first_callback['last_run_date'])
        self.assertEqual(len(first_callback['events']), 1)
        self.assertEqual(first_callback['events'][0]['creditsafe_id'], 'UK-11111111')
        self.assertEqual(len(first_callback['raw_data']), 1)

        second_callback = json.loads(responses.calls[4].request.body.decode('utf-8'))

        self.assertEqual(second_callback['institution_config_id'], str(institution_config_id_2))
        self.assertEqual(second_callback['portfolio_id'], 22222222)
        self.assertIsNotNone(second_callback['last_run_date'])
        self.assertEqual(len(second_callback['events']), 1)
        self.assertEqual(second_callback['events'][0]['creditsafe_id'], 'UK-2222222')
        self.assertEqual(len(second_callback['raw_data']), 1)


    @responses.activate
    def test_callback_error(self):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={
                "totalCount": 1,
                "data": [
                    {
                        "company": {
                            "id": "UK-11111111",
                            "safeNumber": "US22384484",
                            "name": "GOOGLE LLC",
                            "countryCode": "US",
                            "portfolioId": 111111111,
                            "portfolioName": "Default"
                        },
                        "eventId": 101010101,
                        "eventDate": (self.test_end_date - timedelta(seconds=1)).isoformat(),
                        "notificationEventId": randint(1, 9999999999),
                        "ruleCode": 101,
                        "ruleName": "Address"
                    }
                ],
                "paging": {
                    "size": 1000,
                    "prev": None,
                    "next": None,
                    "last": 0
                }
            },
            status=200
        )

        responses.add(
            responses.POST,
            'http://flask:9090/creditsafe/ongoing_monitoring',
            status=500)

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request()
        )

        self.assertEqual(monitoring_events_response.status_code, 500)

    @responses.activate
    def test_bad_request(self):
        self.mock_creditsafe_monitoring_events_response(400, {
            'message': 'Bad request'
        })

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request()
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertIn('Bad request', monitoring_events_response.json['errors'][0]['message'])

    @responses.activate
    def test_not_found(self):
        self.mock_creditsafe_monitoring_events_response(404, {
            'message': 'Not found'
        })

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request()
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertIn('Not found', monitoring_events_response.json['errors'][0]['message'])

    @responses.activate
    def test_access_forbidden(self):
        self.mock_creditsafe_monitoring_events_response(403, {
            'message': 'Access forbidden'
        })

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request()
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertIn('The request could not be authorised: Access forbidden', monitoring_events_response.json['errors'][0]['message'])

    @responses.activate
    def test_unhandled_error(self):
        self.mock_creditsafe_monitoring_events_response(500, {
            'message': 'Unhandled error'
        })

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request()
        )

        self.assertEqual(monitoring_events_response.status_code, 200)
        self.assertIn(
            "The provider returned an error when running this check: 'Unhandled error' while running 'Creditsafe' service. Please get in touch for more information",
            monitoring_events_response.json['errors'][0]['message']
        )

    @mock.patch('app.request_handler.CreditSafeHandler._send_monitoring_callback')
    @responses.activate
    def test_last_run_date_too_recent(self, callback_mock):
        responses.add(
            responses.GET,
            'https://connect.creditsafe.com/v1/monitoring/notificationEvents',
            json={},
            status=200
        )

        configs = [
            {
                'institution_config_id': uuid.uuid4(),
                'portfolio_id': 1010101010,
                'last_run_date': (datetime.now() - timedelta(hours=23)).isoformat()
            },
            {
                'institution_config_id': uuid.uuid4(),
                'portfolio_id': 123454321,
                'last_run_date': self.test_start_date.isoformat()
            }]

        monitoring_events_response = self.app.post(
            '/monitoring_events',
            json=self.get_mock_request(configs)
        )

        # Does not check for events if any last run date is too recent
        self.assertEqual(len(responses.calls), 0)
        self.assertEqual(callback_mock.call_count, 0)

        self.assertEqual(monitoring_events_response.status_code, 200)
