import unittest

from ..file_utils import get_response_from_file
from .internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport, CompanyDirectorsReport, \
    build_resolver_id, PersonOfSignificantControl, CreditsafeSingleShareholder
from .types import SearchInput, Financials
from .internal_types import AssociateIdDeduplicator, process_associate_data, ProcessQueuePayload


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
                "description": "The company knows or has reasonable cause to believe that there is no "
                               "registrable person or registrable relevant legal entity in relation to the company"
            }
        })
        psc.validate()
        self.assertIsNone(psc.name)


class TestCompanyReport(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.passfort_report = get_response_from_file('passfort', folder='demo_data/reports')
        cls.report = CreditSafeCompanyReport.from_json(cls.passfort_report['report'])

        cls.formatted_report = cls.report.as_passfort_format_41()
        cls.maxDiff = None

    def get_associates_by_role(self, role, report=None):
        formatted_report = report or self.formatted_report
        return [
            a for a in formatted_report['associated_entities']
            if any(r['associated_role'] == role for r in a['relationships'])
        ]

    def test_returns_company_metadata(self):
        self.assertEqual(
            self.formatted_report['metadata']['name'],
            'PASSFORT LIMITED'
        )
        self.assertEqual(
            self.formatted_report['metadata']['number'],
            '09565115'
        )
        self.assertEqual(
            self.formatted_report['metadata']['addresses'],
            [
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
            ]
        )
        self.assertEqual(
            self.formatted_report['metadata']['country_of_incorporation'],
            'GBR'
        )
        self.assertEqual(
            self.formatted_report['metadata']['is_active'],
            True
        )
        self.assertEqual(
            self.formatted_report['metadata']['incorporation_date'],
            '2015-04-28'
        )
        self.assertEqual(
            self.formatted_report['metadata']['company_type'],
            'Private limited with Share Capital'
        )
        self.assertEqual(
            self.formatted_report['metadata']['structured_company_type'],
            {
                'is_limited': True,
                'is_public': False
            }
        )
        self.assertEqual(
            self.formatted_report['financials']['contract_limit'],
            {
                'currency_code': 'GBP', 'value': 49500.0
            }
        )
        self.assertEqual(
            self.formatted_report['financials']['credit_history'],
            [
                {
                    'credit_limit': {'currency_code': 'GBP', 'value': 33000.0},
                    'credit_rating': {'value': '96', 'description': 'Very Low Risk'},
                    'international_rating': {'value': 'A', 'description': 'Very Low Risk'},
                    'date': '2018-03-08 23:56:33'
                },
                {
                    'credit_limit': {'currency_code': 'GBP', 'value': 25000.0},
                    'credit_rating': {'value': '87', 'description': 'Very Low Risk'},
                    'international_rating': {'value': 'A', 'description': 'Very Low Risk'},
                    'date': '2017-03-04 22:36:27'
                },
                {
                    'credit_limit': {'currency_code': 'GBP', 'value': 46000.0},
                    'credit_rating': {'value': '95', 'description': 'Very Low Risk'},
                    'date': '2016-08-02 03:41:18'
                },
                {
                    'credit_limit': {'currency_code': 'GBP', 'value': 500.0},
                    'credit_rating': {'value': '47', 'description': 'Moderate Risk'},
                    'date': '2016-07-07 12:44:15'
                },
                {
                    'credit_limit': {'currency_code': 'GBP', 'value': 500.0},
                    'credit_rating': {'value': '49', 'description': 'Moderate Risk'},
                    'date': '2015-04-30 15:13:03'
                }
            ]
        )

        self.assertEqual(
            self.formatted_report['financials']['statements'][0],
            {
                'currency_code': 'GBP',
                'date': '2017-12-31',
                'entries': [
                    {
                        'group_name': 'profit_before_tax',
                        'name': 'depreciation',
                        'value': {
                            'currency_code': 'GBP',
                            'value': 7953.0,
                        },
                        'value_type': 'CURRENCY'
                    },
                    {
                        'group_name': 'profit_before_tax',
                        'name': 'audit_fees',
                        'value': {
                            'currency_code': 'GBP',
                            'value': 0.0,
                        },
                        'value_type': 'CURRENCY'
                    }
                ],
                'groups': [
                    {
                        'name': 'turnover',
                        'value': {
                            'currency_code': 'GBP',
                        },
                        'value_type': 'CURRENCY'
                    },
                    {
                        'name': 'operating_profit',
                        'value': {
                            'currency_code': 'GBP',
                        },
                        'value_type': 'CURRENCY'
                    },
                    {
                        'name': 'profit_before_tax',
                        'value': {
                            'currency_code': 'GBP',
                        },
                        'value_type': 'CURRENCY'
                    },
                    {
                        'name': 'retained_profit',
                        'value': {
                            'currency_code': 'GBP',
                        },
                        'value_type': 'CURRENCY'
                    }],
                'statement_type': 'PROFIT_AND_LOSS'
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
            report.as_passfort_format_41()['metadata'],
            {
                'name': 'PASSFORT LIMITED',
                'number': '09565115',
                'company_type': 'Unknown',
                'country_of_incorporation': 'GBR'
            }
        )

    def test_returns_officers_that_are_companies(self):
        company_officer = self.get_associates_by_role('COMPANY_SECRETARY')[0]

        self.assertDictEqual(
            company_officer,
            {
                'associate_id': str(build_resolver_id('918883145')),
                'entity_type': 'COMPANY',
                'provider_name': 'Creditsafe',
                'immediate_data': {
                    'metadata': {
                        'name': 'CC SECRETARIES LIMITED'
                    },
                    'entity_type': 'COMPANY',
                },
                'relationships': [
                    {
                        'appointed_on': '2018-08-07',
                        'associated_role': 'COMPANY_SECRETARY',
                        'original_role': 'Company Secretary',
                        'relationship_type': 'OFFICER',
                        'is_active': True
                    }
                ]
            }
        )

    def test_returns_officers_that_are_individuals(self):
        directors = self.get_associates_by_role('DIRECTOR')
        self.assertEqual(len(directors), 4)
        self.assertDictEqual(
            directors[0],
            {
                'associate_id': str(build_resolver_id('925098862')),
                'entity_type': 'INDIVIDUAL',
                'provider_name': 'Creditsafe',
                'immediate_data': {
                    'personal_details': {
                        'name': {
                            'given_names': ['Tom', 'Kalervo'],
                            'family_name': 'Henriksson'
                        },
                        'dob': '1968-05'
                    },
                    'entity_type': 'INDIVIDUAL',
                },
                'relationships': [
                    {
                        'appointed_on': '2018-08-31',
                        'associated_role': 'DIRECTOR',
                        'original_role': 'Director',
                        'relationship_type': 'OFFICER',
                        'is_active' : True
                    }
                ]
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

        # use to_associate()
        associate = report.current_directors[0].to_associate('INDIVIDUAL', None)
        self.assertEqual(len(associate['relationships']), 2)
        self.assertEqual(associate['relationships'][0]['associated_role'], 'DIRECTOR')
        self.assertEqual(associate['relationships'][1]['associated_role'], 'COMPANY_SECRETARY')
        self.assertEqual(associate['relationships'][0]['relationship_type'], 'OFFICER')
        self.assertEqual(associate['relationships'][1]['relationship_type'], 'OFFICER')

    def test_returns_shareholders(self):
        shareholders = self.get_associates_by_role('SHAREHOLDER')
        self.assertEqual(len(shareholders), 26)

        self.assertDictEqual(
            shareholders[1]['relationships'][0]['shareholdings'][0],
            {
                'share_class': 'ORDINARY',
                'currency': 'GBP',
                'amount': 4100000,
                'percentage': 20.69,
                'provider_name': 'Creditsafe'
            }
        )
        # test against donald
        donald = next(
            d for d in shareholders
            if d['entity_type'] == 'INDIVIDUAL' and
            d['immediate_data']['personal_details']['name']['family_name'] == 'GILLIES'
        )

        with self.subTest('should resolve ids against directors'):

            self.assertEqual(donald['entity_type'], 'INDIVIDUAL')
            self.assertEqual(len(donald['relationships']), 2)
            r_types = [r['relationship_type'] for r in donald['relationships']]
            self.assertListEqual(sorted(r_types), ['OFFICER', 'SHAREHOLDER'])

        with self.subTest('should merge data from all sources'):
            self.assertDictEqual(
                donald['immediate_data'],
                {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'given_names': ['DONALD', 'ANDREW'], # merge with shareholders
                            'family_name': 'GILLIES',
                            'title': 'Mr'
                        },
                        'nationality': 'GBR',  # merge with psc
                        'dob': '1992-05-30'  # merge with directors or psc
                    }
                }
            )

        with self.subTest('should merge shareholders with multiple classes'):
            episode_shareholder = next(
                s for s in shareholders if s['entity_type'] == 'COMPANY' and
                s['immediate_data']['metadata']['name'] == 'EPISODE (GP) LTD')

            shareholder_relationship = episode_shareholder['relationships'][0]
            self.assertEqual(len(shareholder_relationship['shareholdings']), 2)

            self.assertEqual(shareholder_relationship['total_percentage'], 21.14)
            self.assertEqual(shareholder_relationship['shareholdings'][0]['share_class'], 'SEED')
            self.assertEqual(shareholder_relationship['shareholdings'][0]['percentage'], 15.99)
            self.assertEqual(shareholder_relationship['shareholdings'][1]['share_class'], 'PREFERRED A1')
            self.assertEqual(shareholder_relationship['shareholdings'][1]['percentage'], 5.15)

    def test_returns_company_psc(self):
        duedil_report = get_response_from_file('duedil', folder='demo_data/reports')
        report = CreditSafeCompanyReport.from_json(duedil_report['report'])

        formatted_report = report.as_passfort_format_41()
        shareholders = self.get_associates_by_role('SHAREHOLDER', formatted_report)
        oak_shareholder = next(
            s for s in shareholders if s['entity_type'] == 'COMPANY' and
            'OAK' in s['immediate_data']['metadata']['name']
        )
        self.assertEqual(
            oak_shareholder['immediate_data'],
            {
                'entity_type': 'COMPANY',
                'metadata': {
                    'name': 'OAK INVESTMENT PARTNERS XIII L.P.',
                    'country_of_incorporation': 'USA',  # data from PSC report
                    'number': '4704792'  # data from PSC report
                }
            }
        )


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
                'provider_name': 'Creditsafe'
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

    def test_default_entities(self):
        with self.subTest('default for officer is individual'):
            result = process_associate_data(ProcessQueuePayload({
                'officer': {
                    'name': 'John',
                    'positions': [
                        {
                            'position_name': 'Director'
                        }
                    ]
                }
            }), 'GBR')
            self.assertEqual(result.entity_type, 'INDIVIDUAL')
        with self.subTest('default for secretary is company'):
            result = process_associate_data(ProcessQueuePayload({
                'officer': {
                    'name': 'John',
                    'positions': [
                        {
                            'position_name': 'Company Secretary'
                        }
                    ]
                }
            }), 'GBR')
            self.assertEqual(result.entity_type, 'COMPANY')

        with self.subTest('default for director and secretary is individual'):
            result = process_associate_data(ProcessQueuePayload({
                'officer': {
                    'name': 'John',
                    'positions': [
                        {
                            'position_name': 'Director & Company Secretary'
                        }
                    ]
                }
            }), 'GBR')
            self.assertEqual(result.entity_type, 'INDIVIDUAL')


class TestMergingEntities(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.maxDiff = None

    def setUp(self):
        self.individual_officer_deduplicator = AssociateIdDeduplicator(CompanyDirectorsReport({
            'currentDirectors': [
                {
                    'name': 'Named Star',
                    'dob': '1990-01-01T00:00:00Z'
                }
            ]
        }))

        self.unknown_officer_deduplicator = AssociateIdDeduplicator(CompanyDirectorsReport({
            'currentDirectors': [
                {
                    'name': 'Some Star'
                }
            ]
        }))

        self.no_officer_deduplicator = AssociateIdDeduplicator(CompanyDirectorsReport({
            'currentDirectors': []
        }))

    def test_merges_individual_director_with_individual_shareholder(self):
        self.individual_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'named star',
                    'entity_type': 'INDIVIDUAL'
                })
            ]
        )
        associates = self.individual_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].shareholder)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_merges_individual_director_with_unknown_shareholder(self):
        self.individual_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'named star'
                })
            ]
        )
        associates = self.individual_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].shareholder)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_does_not_merge_individual_director_with_company_shareholder(self):
        self.individual_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'named star',
                    'entity_type': 'COMPANY'
                })
            ]
        )
        associates = self.individual_officer_deduplicator.associates()
        self.assertEqual(len(associates), 2)

        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')
        self.assertEqual(associates[1].entity_type, 'COMPANY')
        self.assertTrue(associates[0].associate_id != associates[1].associate_id)

    def test_merges_unknown_director_with_individual_shareholder(self):
        self.unknown_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'some star',
                    'entity_type': 'INDIVIDUAL'
                })
            ]
        )
        associates = self.unknown_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].shareholder)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_merges_unknown_director_with_unknown_shareholder(self):
        self.unknown_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'some star',
                })
            ]
        )
        associates = self.unknown_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].shareholder)
        self.assertEqual(associates[0].entity_type, None)

        self.assertDictEqual(
            process_associate_data(associates[0], 'GBR').serialize(),
            {
                'entity_type': 'INDIVIDUAL',
                'associate_id': str(associates[0].associate_id),
                'provider_name': 'Creditsafe',
                'immediate_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'family_name': 'star',
                            'given_names': ['some']
                        }
                    }
                },
                'relationships': [
                    {
                        'associated_role': 'SHAREHOLDER',
                        'is_active': True,
                        'relationship_type': 'SHAREHOLDER',
                        'total_percentage': 0.0
                    },
                    {
                        'associated_role': 'OTHER',
                        'is_active': True,
                        'original_role': 'Unknown',
                        'relationship_type': 'OFFICER'
                    }
                ]
            }
        )

    def test_merges_unknown_director_with_company_shareholder(self):
        self.unknown_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'some star',
                    'entity_type': 'COMPANY'
                })
            ]
        )
        associates = self.unknown_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].shareholder)
        self.assertEqual(associates[0].entity_type, 'COMPANY')

    def test_merges_individual_director_with_individual_psc(self):
        self.individual_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'named star',
                    'nationality': 'British',
                    'personType': 'Person'
                })
            ]
        )
        associates = self.individual_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].psc)

        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')
        self.assertDictEqual(
            process_associate_data(associates[0], 'GBR').serialize(),
            {
                'entity_type': 'INDIVIDUAL',
                'associate_id': str(associates[0].associate_id),
                'provider_name': 'Creditsafe',
                'immediate_data': {
                    'entity_type': 'INDIVIDUAL',
                    'personal_details': {
                        'name': {
                            'family_name': 'Star',
                            'given_names': ['Named']
                        },
                        'dob': '1990-01',
                        'nationality': 'GBR'
                    }
                },
                'relationships': [
                    {
                        'associated_role': 'OTHER',
                        'is_active': True,
                        'original_role': 'Unknown',
                        'relationship_type': 'OFFICER'
                    },
                    {
                        'associated_role': 'BENEFICIAL_OWNER',
                        'is_active': True,
                        'relationship_type': 'SHAREHOLDER'
                    }
                ]
            }
        )

    def test_merges_unknown_director_with_individual_psc(self):
        self.unknown_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'some star',
                    'nationality': 'British',
                    'personType': 'Person'
                })
            ]
        )
        associates = self.unknown_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_merges_unknown_director_with_company_psc(self):
        self.unknown_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'some star',
                    'personType': 'Company'
                })
            ]
        )
        associates = self.unknown_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'COMPANY')

    def test_does_not_merge_individual_director_with_company_psc(self):
        self.individual_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'named star',
                    'personType': 'Company'
                })
            ]
        )
        associates = self.individual_officer_deduplicator.associates()
        self.assertEqual(len(associates), 2)

        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[1].psc)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')
        self.assertEqual(associates[1].entity_type, 'COMPANY')

    def test_merges_individual_shareholder_with_individual_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar',
                    'entity_type': 'INDIVIDUAL'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Person'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_merges_company_shareholder_with_company_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar',
                    'entity_type': 'COMPANY'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Company'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'COMPANY')

    def test_merges_unknown_shareholder_with_individual_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Person'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')

    def test_merges_unknown_shareholder_with_company_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Company'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 1)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'COMPANY')

    def test_does_not_merge_individual_shareholder_with_company_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar',
                    'entity_type': 'INDIVIDUAL'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Company'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 2)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[1].psc)
        self.assertEqual(associates[0].entity_type, 'INDIVIDUAL')
        self.assertEqual(associates[1].entity_type, 'COMPANY')

    def test_does_not_merge_company_shareholder_with_individual_psc(self):
        self.no_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'galaxy bar',
                    'entity_type': 'COMPANY'
                })
            ]
        )
        self.no_officer_deduplicator.add_pscs(
            [
                PersonOfSignificantControl({
                    'name': 'galaxy bar',
                    'personType': 'Person'
                })
            ]
        )
        associates = self.no_officer_deduplicator.associates()
        self.assertEqual(len(associates), 2)

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[1].psc)
        self.assertEqual(associates[0].entity_type, 'COMPANY')
        self.assertEqual(associates[1].entity_type, 'INDIVIDUAL')


class TestFinancials(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.base_metadata = {
            'companyId': 'xyz',
            'companySummary': {
                'businessName': 'TEST',
                'country': 'GB',
                'companyNumber': 'UK124',
                'companyRegistrationNumber': '01234',
                'companyStatus': {}
            },
            'companyIdentification': {
                'basicInformation': {
                    'registeredCompanyName': 'TEST',
                    'companyRegistrationNumber': '01234',
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
        }
        cls.maxDiff = None
    
    def test_handles_missing_entries(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'additionalInformation': {
                'creditLimitHistory': [
                    {
                        'companyValue': {
                            'currency': 'GBP',
                            'value': 0
                        },
                        'date': '2011-03-29T00:00:00Z'
                    },
                    {
                        'companyValue': {
                            'currency': 'GBP',
                            'value': 0
                        },
                        'date': '2009-08-27T00:00:00Z'
                    }
                ],
                'ratingHistory': [
                    {
                        "companyValue": 6,
                        "date": "2011-03-29T00:00:00Z",
                        "ratingDescription": "High Risk"
                    },
                    {
                        "companyValue": 32,
                        "date": "2010-09-20T00:00:00Z",
                        "ratingDescription": "Moderate Risk"
                    },
                    {
                        "companyValue": 33,
                        "date": "2010-04-26T00:00:00Z",
                        "ratingDescription": "Moderate Risk"
                    },
                    {
                        "companyValue": 21,
                        "date": "2009-08-20T00:00:00Z",
                        "ratingDescription": "High Risk"
                    }
                ]
            }
        })

        # Handles dates and lengths not being the same
        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [
                    {
                        'date': '2011-03-29 00:00:00',
                        'credit_limit': {'currency_code': 'GBP', 'value': 0.0},
                        'credit_rating': {'value': '6', 'description': 'High Risk'}
                    },
                    {
                        'date': '2010-09-20 00:00:00',
                        'credit_rating': {'value': '32', 'description': 'Moderate Risk'}
                    },
                    {
                        'date': '2010-04-26 00:00:00',
                        'credit_rating': {'value': '33', 'description': 'Moderate Risk'}
                    },
                    {
                        'date': '2009-08-27 00:00:00',
                        'credit_limit': {'currency_code': 'GBP', 'value': 0.0},
                    },
                    {
                        'date': '2009-08-20 00:00:00',
                        'credit_rating': {'value': '21', 'description': 'High Risk'}
                    }
                ]
            }
        )

    def test_handles_missing_value_and_description(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'creditScore': {
                'currentCreditRating': {
                },
            },
            'additionalInformation': {
                'creditLimitHistory': [
                    {
                        'companyValue': {
                            'currency': 'GBP',
                        },
                        'date': '2011-03-29T00:00:00Z'
                    }
                ],
                'ratingHistory': [
                    {
                        "date": "2011-03-29T00:00:00Z",
                    }
                ]
            }
        })

        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [{
                    'date': '2011-03-29 00:00:00'
                }]
            }
        )

    def test_handles_bad_currency(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'additionalInformation': {
                'creditLimitHistory': [
                    {
                        'companyValue': {
                            'currency': 'WHO',
                            'value': 0
                        },
                        'date': '2011-03-29T00:00:00Z'
                    }
                ]
            }
        })

        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [{
                    'date': '2011-03-29 00:00:00'
                }]
            }
        )

    def test_ignores_missing_description(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'creditScore': {
                'currentCreditRating': {
                   'commonValue': 'A'
                },
                'previousCreditRating': {
                    'commonValue': 'B'
                }
            },
            'additionalInformation': {
                'ratingHistory': [
                    {
                        "value": 20,
                        "date": "2011-03-29T00:00:00Z",
                    }
                ]
            }
        })

        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [{
                    'date': '2011-03-29 00:00:00',
                    'credit_rating': {'value': '20'},
                    'international_rating': {'value': 'A'}
                }]
            }
        )
