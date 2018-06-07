import unittest
import os
import responses  # type: ignore
import requests
from schemad_types.utils import get_in

from flask import json
from app.charities import format_trustee, get_charity
from dassert import Assert


class TestCharities(unittest.TestCase):
    base_url = "https://duedil.io/v4{}"

    def mock_request(self, url=None, method=responses.GET, **kwargs):
        responses.add(
            method,
            self.base_url.format(url),
            **kwargs
        )

    def mock_all_requests(self):
        self.mock_request(
            url='/search/charities.json',
            method=responses.POST,
            json=create_search_response()
        )
        self.mock_request(
            url='/charity/gb/ew-261017-0.json',
            json=create_vitals_response()
        )
        self.mock_request(
            url='/charity/gb/ew-261017-0/trustees.json',
            json=create_trustees_response()
        )
        self.mock_request(
            url='/charity/gb/ew-261017-0/classifiers.json',
            json=create_classifiers_response()
        )
        self.mock_request(
            url='/charity/gb/ew-261017-0/areas-of-activity.json',
            json=create_areas_of_activity_response()
        )

    @responses.activate
    def test_it_requests_charities_metadata(self):
        self.mock_all_requests()

        raw, response = get_charity('gb', '02400969', {})
        Assert.equal(response['metadata'], {
            'name': 'Macmillan Cancer Support',
            'number': '02400969',
            'charity_number': '261017',
            'addresses': [
                {
                    'type': 'contact_address',
                    'address': {
                        'type': 'STRUCTURED',
                        'original_freeform_address': 'Macmillan Cancer Support, 89 Albert Embankment, London, SE1 7UQ'
                    }
                }
            ],
            'country_of_incorporation': 'GBR',
            'number_of_employees': 1642,
            'is_active': True,
            'contact_details': {
                'email': 'henry@passfort.com',
                'phone_number': '0123456789',
                'url': 'macmillan.org.uk'
            },
            'areas_of_activity': [
                {'location': 'Throughout England and Wales'},
                {'location': 'Solomon Islands'},
                {'location': 'Northern Ireland'},
                {'location': 'Jersey'},
                {'location': 'St Barthelemy'},
                {'location': 'India'}
            ],
            'description': 'TO PROVIDE SUPPORT, ASSISTANCE AND INFORMATION DIRECTLY OR INDIRECTLY TO PEOPLE AFFECTED '
                           'BY CANCER; TO FURTHER AND BUILD CANCER AWARENESS, EDUCATION AND RESEARCH; TO PROMOTE AND '
                           'INFLUENCE EFFECTIVE CARE, INVOLVEMENT AND SUPPORT FOR PEOPLE AFFECTED BY CANCER'
        })

    @responses.activate
    def test_it_requests_charities_officers(self):
        self.mock_all_requests()

        raw, response = get_charity('gb', '02400969', {})
        Assert.equal(len(response['officers']['trustees']), 20)
        Assert.equal(response['officers']['trustees'][0], {
            'immediate_data': {
                'entity_type': 'INDIVIDUAL',
                'personal_details': {
                    'name': {
                        'title': 'Dr',
                        'given_names': ['Jagjit', 'Singh'],
                        'family_name': 'Ahluwalia'
                    }
                }
            },
            'entity_type': 'INDIVIDUAL',
            'provider_name': 'DueDil'
        })
        Assert.equal(response['officers']['trustees'][-1], {
            'immediate_data': {
                'entity_type': 'INDIVIDUAL',
                'personal_details': {
                    'name': {
                        'title': 'Ms',
                        'given_names': ['Susan', 'Carol'],
                        'family_name': 'Langley'
                    }
                },
            },
            'entity_type': 'INDIVIDUAL',
            'provider_name': 'DueDil'
        })

    @responses.activate
    def test_it_requests_charities_charity_data(self):
        self.mock_all_requests()

        raw, response = get_charity('gb', '02400969', {})
        Assert.equal(response['charity_data'], {
            'registration_date': '1989-06-21',
            'number_of_volunteers': 20000,
            'beneficiaries': [
                'People of A Particular Ethnic Or Racial Origin',
                'Other Charities Or Voluntary Bodies',
                'The General Public/Mankind',
                'Other Defined Groups',
                'Children/Young People',
                'People With Disabilities',
                'Elderly/Old People',
            ],
            'activity': [
                'Sponsors Or Undertakes Research',
                'Makes Grants To Organisations',
            ],
            'purpose': [
                'Education/Training'
            ]
        })

    @responses.activate
    def test_it_requests_charities_financials(self):
        self.mock_all_requests()

        raw, response = get_charity('gb', '02400969', {})
        Assert.equal(response['financials'], {
            'total_income_and_endowments': {'value': 247441000, 'currency_code': 'GBP'},
            'total_expenditure': {'value': 245591000, 'currency_code': 'GBP'},
            'total_funds': {'value': 64302000, 'currency_code': 'GBP'}
        })


class TestFormatTrustees(unittest.TestCase):
    base_url = "https://duedil.io/v4{}"

    def mock_get(self, url=None, **kwargs):
        responses.add(
            responses.GET,
            self.base_url.format(url),
            **kwargs
        )

    @responses.activate
    def test_it_formats_individual_trustees(self):
        result = format_trustee({'sourceName': 'Mr Henry Irish'})
        Assert.equal(result['immediate_data']['personal_details']['name']['given_names'], ['Henry'])
        Assert.equal(result['immediate_data']['personal_details']['name']['family_name'], 'Irish')

    @responses.activate
    def test_it_formats_individual_trustees_with_multiple_forenames(self):
        result = format_trustee({'sourceName': 'Mr Henry Bob Irish'})
        Assert.equal(result['immediate_data']['personal_details']['name']['given_names'], ['Henry', 'Bob'])
        Assert.equal(result['immediate_data']['personal_details']['name']['family_name'], 'Irish')

    # @responses.activate
    # def test_it_formats_company_trustees(self):
    #     result = format_trustee({'sourceName': 'Henry Bob Irish'})
    #     Assert.equal(result['immediate_data']['personal_details']['name']['given_names'], ['Henry', 'Bob'])


def create_search_response():
    with open("./demo_data/charities_search.json", 'rb') as f:
        return json.loads(f.read())


def create_vitals_response():
    with open("./demo_data/charity_vitals.json", 'rb') as f:
        return json.loads(f.read())


def create_trustees_response():
    with open("./demo_data/charity_trustees.json", 'rb') as f:
        return json.loads(f.read())


def create_classifiers_response():
    with open("./demo_data/charity_classifiers.json", 'rb') as f:
        return json.loads(f.read())


def create_areas_of_activity_response():
    with open("./demo_data/charity_areas_of_activity.json", 'rb') as f:
        return json.loads(f.read())
