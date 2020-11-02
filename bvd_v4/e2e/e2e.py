import unittest
import requests
import responses

API_URL = "http://localhost:8001"
COMPANY_DATA_URL = API_URL + "/company-data-check"
CREATE_PORTFOLIO_URL = API_URL + "/monitoring_portfolio"
ADD_TO_PORTFOLIO_URL = API_URL + "/monitoring"

from app.common import build_resolver_id
from app.application import app


class TestDemoRequest(unittest.TestCase):
    def test_health_endpoint(self):
        response = requests.get(API_URL + "/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "success")

    def test_demo_company_data(self):
        response = requests.post(
            COMPANY_DATA_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"country_of_incorporation": "GBR", "bvd_id": "pass"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["metadata"]["name"], "PASSFORT LIMITED"
        )
        self.assertEqual(response.json()["output_data"]["metadata"]["bvd_id"], "pass")

    def test_create_monitoring_portfolio(self):
        response = requests.post(
            CREATE_PORTFOLIO_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"name": "d1c3f995-e502-457d-9f58-7bc75a242769"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["id"], "4ed92e40-a501-eb11-90b5-d89d672fa480"
        )

    def test_add_to_monitoring_portfolio(self):
        response = requests.post(
            ADD_TO_PORTFOLIO_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {
                    "portfolio_id": "4ed92e40-a501-eb11-90b5-d89d672fa480",
                    "bvd_id": "pass",
                },
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["id"], "4ed92e40-a501-eb11-90b5-d89d672fa480"
        )


    def test_company_data_associate_ids(self):
        response = requests.post(
            COMPANY_DATA_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"country_of_incorporation": "GBR", "bvd_id": "pass"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])

        # Test merges to expected number of associates
        self.assertEqual(
            len(response.json()["output_data"]["associated_entities"]),
            30
        )

        shareholder_with_bvd_id = next((
            entity for entity in
            response.json()["output_data"]["associated_entities"]
            if entity['immediate_data'].get('metadata', {}).get('bvd_id', None) == 'GBLP016464'
        ))
        self.assertEqual(
            shareholder_with_bvd_id['associate_id'],
            str(build_resolver_id('GBLP016464'))
        )
        self.assertEqual(
            len(shareholder_with_bvd_id['relationships'][0]['shareholdings']),
            1
        )

        self.assertEqual(
            shareholder_with_bvd_id['relationships'][0]['shareholdings'][0]['percentage'],
            4.03
        )
        self.assertEqual(
            shareholder_with_bvd_id['relationships'][0]['total_percentage'],
            4.03
        )

class TestSearchRequest(unittest.TestCase):
    def setUp(self):
        # creates a test client
        self.app = app.test_client()
        # propagate the exceptions to the test client
        self.app.testing = True

    @responses.activate
    def test_search_returns_rate_limit_error(self):
        responses.add(
            responses.GET,
            'https://orbis.bvdinfo.com/api/orbis/Companies/data?QUERY=%7B%22WHERE%22%3A+%5B%7B%22MATCH%22%3A+%7B%22Criteria%22%3A+%7B%22Name%22%3A+%22PassFort%22%2C+%22NationalId%22%3A+%22%22%2C+%22Country%22%3A+%22GB%22%2C+%22State%22%3A+%22%22%7D%7D%7D%5D%2C+%22SELECT%22%3A+%5B%22BVDID%22%2C+%22MATCH.BVD9%22%2C+%22MATCH.NAME%22%2C+%22MATCH.STATUS%22%2C+%22MATCH.NAME_INTERNATIONAL%22%2C+%22MATCH.ADDRESS%22%2C+%22MATCH.POSTCODE%22%2C+%22MATCH.CITY%22%2C+%22MATCH.COUNTRY%22%2C+%22MATCH.NATIONAL_ID%22%2C+%22MATCH.STATE%22%2C+%22MATCH.ADDRESS_TYPE%22%2C+%22MATCH.HINT%22%2C+%22MATCH.SCORE%22%5D%7D',
            status=429)

        result = self.app.post(
            '/search',
            json={
                'credentials': {'key': '123456789'},
                'is_demo': False,
                'input_data': {
                    'country': 'GBR',
                    'name': 'PassFort',
                    'state': '',
                    'number': ''
                }
            }
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['errors']), 1)
        self.assertEqual(result.json['errors'][0]['code'], 302)
        self.assertEqual(
            result.json['errors'][0]['message'],
            "Provider rate limit exceeded"
        )

    @responses.activate
    def test_connection_error(self):
        result = self.app.post(
            '/search',
            json={
                'credentials': {'key': '123456789'},
                'is_demo': False,
                'input_data': {
                    'country': 'GBR',
                    'name': 'PassFort',
                    'state': '',
                    'number': ''
                }
            }
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['errors']), 1)
        self.assertEqual(result.json['errors'][0]['code'], 302)
        self.assertEqual(
            result.json['errors'][0]['message'],
            "Failed to connect to provider"
        )

    @responses.activate
    def test_bad_provider_response(self):
        responses.add(
            responses.GET,
            'https://orbis.bvdinfo.com/api/orbis/Companies/data?QUERY=%7B%22WHERE%22%3A+%5B%7B%22MATCH%22%3A+%7B%22Criteria%22%3A+%7B%22Name%22%3A+%22PassFort%22%2C+%22NationalId%22%3A+%22%22%2C+%22Country%22%3A+%22GB%22%2C+%22State%22%3A+%22%22%7D%7D%7D%5D%2C+%22SELECT%22%3A+%5B%22BVDID%22%2C+%22MATCH.BVD9%22%2C+%22MATCH.NAME%22%2C+%22MATCH.STATUS%22%2C+%22MATCH.NAME_INTERNATIONAL%22%2C+%22MATCH.ADDRESS%22%2C+%22MATCH.POSTCODE%22%2C+%22MATCH.CITY%22%2C+%22MATCH.COUNTRY%22%2C+%22MATCH.NATIONAL_ID%22%2C+%22MATCH.STATE%22%2C+%22MATCH.ADDRESS_TYPE%22%2C+%22MATCH.HINT%22%2C+%22MATCH.SCORE%22%5D%7D',
            json={'bad': 'response'},
            status=200)

        result = self.app.post(
            '/search',
            json={
                'credentials': {'key': '123456789'},
                'is_demo': False,
                'input_data': {
                    'country': 'GBR',
                    'name': 'PassFort',
                    'state': '',
                    'number': ''
                }
            }
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['errors']), 1)
        self.assertEqual(result.json['errors'][0]['code'], 303)
        self.assertEqual(
            result.json['errors'][0]['message'],
            "Provider returned data in an unexpected format"
        )

    @responses.activate
    def test_bad_provider_response(self):
        responses.add(
            responses.GET,
            'https://orbis.bvdinfo.com/api/orbis/Companies/data?QUERY=%7B%22WHERE%22%3A+%5B%7B%22MATCH%22%3A+%7B%22Criteria%22%3A+%7B%22Name%22%3A+%22PassFort%22%2C+%22NationalId%22%3A+%22%22%2C+%22Country%22%3A+%22GB%22%2C+%22State%22%3A+%22%22%7D%7D%7D%5D%2C+%22SELECT%22%3A+%5B%22BVDID%22%2C+%22MATCH.BVD9%22%2C+%22MATCH.NAME%22%2C+%22MATCH.STATUS%22%2C+%22MATCH.NAME_INTERNATIONAL%22%2C+%22MATCH.ADDRESS%22%2C+%22MATCH.POSTCODE%22%2C+%22MATCH.CITY%22%2C+%22MATCH.COUNTRY%22%2C+%22MATCH.NATIONAL_ID%22%2C+%22MATCH.STATE%22%2C+%22MATCH.ADDRESS_TYPE%22%2C+%22MATCH.HINT%22%2C+%22MATCH.SCORE%22%5D%7D',
            body='not json',
            status=200)

        result = self.app.post(
            '/search',
            json={
                'credentials': {'key': '123456789'},
                'is_demo': False,
                'input_data': {
                    'country': 'GBR',
                    'name': 'PassFort',
                    'state': '',
                    'number': ''
                }
            }
        )

        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json['errors']), 1)
        self.assertEqual(result.json['errors'][0]['code'], 303)
        self.assertEqual(
            result.json['errors'][0]['message'],
            "Provider returned data in an unexpected format"
        )
