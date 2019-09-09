import unittest

from ..file_utils import get_response_from_file
from .internal_types import CreditSafeCompanyReport, CompanyDirectorsReport


class TestCompanyReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.passfort_report = get_response_from_file('passfort', folder='demo_data/reports')
        cls.report = CreditSafeCompanyReport.from_json(cls.passfort_report['report'])

        cls.formatted_report = cls.report.as_passfort_format()
        cls.maxDiff = None

    def test_returns_company_metadata(self):
        self.assertDictEqual(
            self.formatted_report['metadata'],
            {
                'name': 'PASSFORT LIMITED',
                'number': '09565115',
                'addresses': [
                    {
                        'type': 'registered_address',
                        'address': {
                            'type': 'FREEFORM',
                            'text': 'THE STUDIO 11 PRINCELET STREET, LONDON, E1 6QH',
                            'country': None
                        }
                    },
                    {
                        'type': 'trading_address',
                        'address': {
                            'type': 'FREEFORM',
                            'text': 'The Studio 11 Princelet Street, London, E1 6QH',
                            'country': None
                        }
                    },
                    {
                        'type': 'trading_address',
                        'address': {
                            'type': 'FREEFORM',
                            'text': 'Unit 418, The Print Rooms, 164/180 Union Street, London, SE1 0LH',
                            'country': None
                        }
                    }
                ],
                'country_of_incorporation': 'GBR',
                'is_active': True,
                'incorporation_date': '2015-04-28 00:00:00',
                'company_type': 'Private limited with Share Capital',
                'structured_company_type': {
                    'is_limited': True,
                    'is_public': False,
                    'ownership_type': None,
                }

            }
        )

    def test_returns_officers_that_are_companies(self):
        company_officer = self.formatted_report['officers']['secretaries'][0]
        self.assertDictEqual(
            company_officer,
            {
                'resolver_id': '918883145',
                'type': 'COMPANY',
                'first_names': None,
                'last_name': 'CC SECRETARIES LIMITED',
                'original_role': 'Company Secretary',
                'appointed_on': '2018-08-07 00:00:00',
                'provider_name': 'CreditSafe'
            }
        )

    def test_returns_officers_that_are_individuals(self):
        directors = self.formatted_report['officers']['directors']
        self.assertEqual(len(directors), 4)
        self.assertDictEqual(
            directors[0],
            {
                'resolver_id': '925098862',
                'type': 'INDIVIDUAL',
                'first_names': ['Tom', 'Kalervo'],
                'last_name': 'Henriksson',
                'original_role': 'Director',
                'appointed_on': '2018-08-31 00:00:00',
                'provider_name': 'CreditSafe',
                'dob': '1968-05-01 00:00:00'
            }
        )

    def test_handles_umbrella_positions(self):
        report = CompanyDirectorsReport().import_data({
            "currentDirectors": [
                {
                    "id": "test",
                    "name": "Mr Bruce Wayne",
                    "title": "Mr",
                    "firstName": "Bruce",
                    "surname": "Wayne",
                    "address": {
                        "simpleValue": "The Studio 11 Princelet Street, London, E1 6QH",
                        "postalCode": "E1 6QH"
                    },
                    "gender": "Male",
                    "directorType": "Other",
                    "positions": [
                        {
                            "dateAppointed": "2018-08-31T00:00:00Z",
                            "positionName": "Director & Company Secretary"
                        }
                    ]
                }
            ]
        }, apply_defaults=True)

        formatted_report = report.as_passfort_format()
        self.assertEqual(len(formatted_report['directors']), 1)
        self.assertEqual(len(formatted_report['secretaries']), 1)

        self.assertEqual(formatted_report['directors'][0]['resolver_id'], 'test')
        self.assertEqual(formatted_report['secretaries'][0]['resolver_id'], 'test')
