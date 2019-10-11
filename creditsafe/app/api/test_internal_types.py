import unittest
import uuid

from ..file_utils import get_response_from_file
from .internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport, CompanyDirectorsReport, \
    build_resolver_id, PersonOfSignificantControl
from .types import SearchInput
from .internal_types import AssociateIdDeduplicator, process_associate_data


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


class TestPSC(unittest.TestCase):
    def test_country_of_incorporation(self):
        psc = PersonOfSignificantControl({
            'name': 'Test',
            'personType': 'Company',
            'country': 'England'
        })
        self.assertEqual(psc.country_of_incorporation, 'GBR')

        psc = PersonOfSignificantControl({
            'name': 'Test',
            'personType': 'Company',
            'country': 'United States'
        })
        self.assertEqual(psc.country_of_incorporation, 'USA')

        psc = PersonOfSignificantControl({
            'name': 'Test',
            'personType': 'Company',
            'countryOfRegistration': 'United States of America'
        })
        self.assertEqual(psc.country_of_incorporation, 'USA')

        psc = PersonOfSignificantControl().import_data({
            "address": {
                "city": "London",
                "houseNumber": "83",
                "postalCode": "SW1H 0HW",
                "simpleValue": "83, Victoria Street, London, England",
                "street": "Victoria Street"
            },
            "country": "England",
            "countryOfRegistration": "England & Wales",
            "governingLaw": "English",
            "insertDate": "2019-10-09T20:11:13Z",
            "kind": "corporate-entity-person-with-significant-control",
            "legalForm": "Limited Company",
            "name": "Venture Founders Limited",
            "natureOfControl": "ownership-of-shares-75-to-100-percent,voting-rights-75-to-100-percent",
            "notifiedOn": "2016-04-06T00:00:00Z",
            "personType": "Company",
            "placeRegistered": "Companies House",
            "registrationNumber": "8636143"
        })
        self.assertEqual(psc.country_of_incorporation, 'GBR')

    def test_handles_statement_returned_instead_of_psc(self):
        psc = PersonOfSignificantControl().import_data({
            "insertDate": "2019-10-10T20:23:57Z",
            "kind": "persons-with-significant-control-statement",
            "notifiedOn": "2018-03-13T00:00:00Z",
            "statement": {
                "code": "no-individual-or-entity-with-signficant-control",
                "description": "The company knows or has reasonable cause to believe that there is no registrable person or registrable relevant legal entity in relation to the company"
            }
        })
        psc.validate()
        self.assertIsNone(psc.name)


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
                s['immediate_data']['personal_details']['name']['family_name'] == 'GILLIES' and
                s.get('shareholdings')
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

            self.assertEqual(episode_shareholder['total_percentage'], 21.14)
            self.assertEqual(episode_shareholder['shareholdings'][0]['share_class'], 'SEED')
            self.assertEqual(episode_shareholder['shareholdings'][0]['percentage'], 15.99)
            self.assertEqual(episode_shareholder['shareholdings'][1]['share_class'], 'PREFERRED A1')
            self.assertEqual(episode_shareholder['shareholdings'][1]['percentage'], 5.15)


class TestDuplicateResolver(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.passfort_report = get_response_from_file('passfort', folder='demo_data/reports')
        cls.report = CreditSafeCompanyReport.from_json(cls.passfort_report['report'])

        cls.maxDiff = None

    def test_deduplicates_shareholders(self):
        duplicate_resolver = AssociateIdDeduplicator(self.report.directors)
        unique_shareholders = list(self.report.share_capital_structure.unique_shareholders())

        self.assertEqual(len(unique_shareholders), 26)

        self.assertDictEqual(
            unique_shareholders[1]['shareholdings'][0].serialize(),
            {
                'share_class': 'ORDINARY',
                'currency': 'GBP',
                'amount': 4100000,
                'percentage': 20.69,
                'provider_name': 'CreditSafe'
            }
        )

        duplicate_resolver.add_shareholders(unique_shareholders)
        associates = [process_associate_data(a, 'GBR').serialize() for a in duplicate_resolver.associates()]

        with self.subTest('should resolve ids against directors'):
            # test against donald
            merged = [a for a in associates if len(a['relationships']) > 0]
            donald = next(
                d for d in merged
                if d['entity_type'] == 'INDIVIDUAL' and
                d['immediate_data']['personal_details']['name']['family_name'].lower() == 'gillies'
            )
            self.assertEqual(len(donald['relationships']), 2)
            r_types = [r['relationship_type'] for r in donald['relationships']]
            self.assertListEqual(sorted(r_types), ['OFFICER', 'SHAREHOLDER'])

            self.assertEqual(
                donald['immediate_data']['personal_details']['name']['given_names'],
                ['DONALD', 'ANDREW']
            )

            self.assertEqual(donald['entity_type'], 'INDIVIDUAL')

        with self.subTest('should merge shareholders with multiple classes'):
            episode_shareholder = next(
                s for s in associates if s['entity_type'] == 'COMPANY' and
                s['immediate_data']['metadata']['name'] == 'EPISODE (GP) LTD')
            shareholder_relationship = episode_shareholder['relationships'][0]
            self.assertEqual(len(shareholder_relationship['shareholdings']), 2)

            self.assertEqual(shareholder_relationship['total_percentage'], 21.14)
            self.assertEqual(shareholder_relationship['shareholdings'][0]['share_class'], 'SEED')
            self.assertEqual(shareholder_relationship['shareholdings'][0]['percentage'], 15.99)
            self.assertEqual(shareholder_relationship['shareholdings'][1]['share_class'], 'PREFERRED A1')
            self.assertEqual(shareholder_relationship['shareholdings'][1]['percentage'], 5.15)

    def test_deduplicates_psc(self):
        duplicate_resolver = AssociateIdDeduplicator(self.report.directors)
        unique_shareholders = list(self.report.share_capital_structure.unique_shareholders())
        duplicate_resolver.add_shareholders(unique_shareholders)
        duplicate_resolver.add_pscs(self.report.additional_information.psc_report.active_psc)
        associates = [process_associate_data(a, 'GBR').serialize() for a in duplicate_resolver.associates()]

        donald = next(
            s for s in associates if s['entity_type'] == 'INDIVIDUAL' and
            s['immediate_data']['personal_details']['name']['family_name'].lower() == 'gillies'
        )

        self.assertIsNotNone(donald)
        # Field from psc
        self.assertEqual(donald['immediate_data']['personal_details']['nationality'], 'GBR')

        self.assertEqual(len(donald['relationships']), 2)
        r_types = [r['relationship_type'] for r in donald['relationships']]
        self.assertListEqual(sorted(r_types), ['OFFICER', 'SHAREHOLDER'])
        a_types = [r['associated_role'] for r in donald['relationships']]
        self.assertListEqual(sorted(a_types), ['DIRECTOR', 'SHAREHOLDER'])
