import unittest

from ..file_utils import get_response_from_file
from .internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport, CompanyDirectorsReport, build_resolver_id
from .types import SearchInput


class TestCompanySearchResponse(unittest.TestCase):
    def test_name_matching_less_strict_if_number_matches(self):
        searchResp = CreditSafeCompanySearchResponse.from_json({
            'creditsafe_id': '1000',
            'regNo': '09565115',
            'name': 'PASSFORT LIMITED',
        })

        # Produces match ratio of 86 which is < 90 but > 50
        self.assertTrue(searchResp.matches_search(SearchInput({
            'name': 'PASSF LMITED',
            'number': '09565115'
        }), fuzz_factor=90))

        self.assertFalse(searchResp.matches_search(SearchInput({
            'name': 'PASSF LMITED',
        }), fuzz_factor=90))


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
                            'country': 'GBR'
                        }
                    },
                    {
                        'type': 'trading_address',
                        'address': {
                            'type': 'FREEFORM',
                            'text': 'The Studio 11 Princelet Street, London, E1 6QH',
                            'country': 'GBR'
                        }
                    }
                ],
                'country_of_incorporation': 'GBR',
                'is_active': True,
                'incorporation_date': '2015-04-28',
                'company_type': 'Private limited with Share Capital',
                'structured_company_type': {
                    'is_limited': True,
                    'is_public': False
                }

            }
        )
        
    def test_handles_missing_data(self):
        report = CreditSafeCompanyReport.from_json({
            'companyId': 'GB001-0-09565115',
            'companySummary': {
                'businessName': 'PASSFORT LIMITED',
                'country': 'GB',
                'companyNumber': 'UK13646576',
                'companyRegistrationNumber': '09565115',
                'companyStatus': {}
            },
            'companyIdentification': {
                'basicInformation': {
                    'registeredCompanyName': 'PASSFORT LIMITED',
                    'companyRegistrationNumber': '09565115',
                    'country': 'GB',
                    'legalForm': {
                        'description': 'Unknown'
                    },
                    'companyStatus': {}
                }
            },
            'contactInformation': {
                'mainAddress': {
                    'type': 'Some Address',
                    'postalCode': 'E1 6QH'
                }
            }
        })

        self.assertDictEqual(
            report.as_passfort_format()['metadata'],
            {
                'name': 'PASSFORT LIMITED',
                'number': '09565115',
                'company_type': 'Unknown',
                'country_of_incorporation': 'GBR'
            }
        )

    def test_returns_officers_that_are_companies(self):
        company_officer = self.formatted_report['officers']['secretaries'][0]
        self.assertDictEqual(
            company_officer,
            {
                'resolver_id': str(build_resolver_id('918883145')),
                'entity_type': 'COMPANY',
                'original_role': 'Company Secretary',
                'appointed_on': '2018-08-07',
                'provider_name': 'CreditSafe',
                'immediate_data': {
                    'metadata': {
                        'name': 'CC SECRETARIES LIMITED'
                    },
                    'entity_type': 'COMPANY',
                }
            }
        )

    def test_returns_officers_that_are_individuals(self):
        directors = self.formatted_report['officers']['directors']
        self.assertEqual(len(directors), 4)
        self.assertDictEqual(
            directors[0],
            {
                'resolver_id': str(build_resolver_id('925098862')),
                'entity_type': 'INDIVIDUAL',
                'original_role': 'Director',
                'appointed_on': '2018-08-31',
                'provider_name': 'CreditSafe',
                'immediate_data': {
                    'personal_details': {
                        'name': {
                            'given_names': ['Tom', 'Kalervo'],
                            'family_name': 'Henriksson'
                        },
                        'dob': '1968-05'
                    },
                    'entity_type': 'INDIVIDUAL',
                }
            }
        )

    def test_handles_umbrella_positions(self):
        report = CompanyDirectorsReport().import_data({
            'currentDirectors': [
                {
                    'id': 'test',
                    'name': 'Mr Bruce Wayne',
                    'title': 'Mr',
                    'firstName': 'Bruce',
                    'surname': 'Wayne',
                    'address': {
                        'simpleValue': 'The Studio 11 Princelet Street, London, E1 6QH',
                        'postalCode': 'E1 6QH'
                    },
                    'gender': 'Male',
                    'directorType': 'Other',
                    'positions': [
                        {
                            'dateAppointed': '2018-08-31T00:00:00Z',
                            'positionName': 'Director & Company Secretary'
                        }
                    ]
                }
            ]
        }, apply_defaults=True)

        formatted_report = report.to_serialized_passfort_format(None, 'GBR')
        self.assertEqual(len(formatted_report['directors']), 1)
        self.assertEqual(len(formatted_report['secretaries']), 1)

        self.assertEqual(formatted_report['directors'][0]['resolver_id'], str(build_resolver_id('test')))
        self.assertEqual(formatted_report['secretaries'][0]['resolver_id'], str(build_resolver_id('test')))

    def test_returns_shareholders(self):
        shareholders = self.formatted_report['ownership_structure']['shareholders']
        self.assertEqual(len(shareholders), 26)

        self.assertDictEqual(
            shareholders[1]['shareholdings'][0],
            {
                'share_class': 'ORDINARY',
                'currency': 'GBP',
                'amount': 4100000,
                'percentage': 20.69,
                'provider_name': 'CreditSafe'
            }
        )

        with self.subTest('should resolve ids against directors'):
            # test against donald
            donald_director = next(
                d for d in self.formatted_report['officers']['directors']
                if d['entity_type'] == 'INDIVIDUAL' and
                d['immediate_data']['personal_details']['name']['family_name'] == 'Gillies'
            )
            donald_shareholder = next(
                s for s in shareholders if s['entity_type'] == 'INDIVIDUAL' and
                s['immediate_data']['personal_details']['name']['family_name'] == 'GILLIES'
            )

            self.assertEqual(
                donald_director['immediate_data']['personal_details']['name']['given_names'],
                ['Donald', 'Andrew']
            )

            self.assertEqual(
                donald_shareholder['immediate_data']['personal_details']['name']['given_names'],
                ['DONALD', 'ANDREW']
            )

            self.assertEqual(donald_shareholder['entity_type'], 'INDIVIDUAL')
            self.assertEqual(donald_director['entity_type'], 'INDIVIDUAL')
            self.assertEqual(donald_director['resolver_id'], donald_shareholder['resolver_id'])

        with self.subTest('should merge shareholders with multiple classes'):
            episode_shareholder = next(
                s for s in shareholders if s['entity_type'] == 'COMPANY' and
                s['immediate_data']['metadata']['name'] == 'EPISODE (GP) LTD')

            self.assertEqual(len(episode_shareholder['shareholdings']), 2)
            print(episode_shareholder['shareholdings'])

            self.assertEqual(episode_shareholder['total_percentage'], 21.14)
            self.assertEqual(episode_shareholder['shareholdings'][0]['share_class'], 'SEED')
            self.assertEqual(episode_shareholder['shareholdings'][0]['percentage'], 15.99)
            self.assertEqual(episode_shareholder['shareholdings'][1]['share_class'], 'PREFERRED A1')
            self.assertEqual(episode_shareholder['shareholdings'][1]['percentage'], 5.15)
