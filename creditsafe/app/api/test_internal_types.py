import unittest

from datetime import datetime, timedelta
from random import randint

from ..file_utils import get_response_from_file
from .internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport, CompanyDirectorsReport, \
    build_resolver_id, PersonOfSignificantControl, CreditsafeSingleShareholder
from .types import SearchInput, Financials, Statement, MonitoringEvent
from .internal_types import AssociateIdDeduplicator, process_associate_data, ProcessQueuePayload, with_yoy, \
    CreditSafeNotificationEventsResponse, CreditSafeNotificationEvent
from .event_mappings import MonitoringConfigType

DEMO_PL = {
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
            'yoy': 2.417705199828105,
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

    def test_no_name_response(self):
        searchResp = CreditSafeCompanySearchResponse.from_json({
            'creditsafe_id': '1000',
            'regNo': '09565115',
        })

        self.assertTrue(searchResp.matches_search(SearchInput({
            'number': '09565115',
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

    def assert_entry_with(self, entry, name, value, group_name=None, yoy=None):
        self.assertEqual(entry['name'], name)

        self.assertEqual(entry['value'].get('value', None), value)

        self.assertEqual(entry.get('group_name', None), group_name)
        self.assertAlmostEqual(entry.get('yoy', None), yoy)

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
                },
                {
                    'type': 'trading_address',
                    'address': {
                        'type': 'FREEFORM',
                        'text': 'Unit 418, The Print Rooms, 164/180 Union Street, London, SE1 0LH',
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

    def test_returns_financials(self):
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

        with self.subTest('returns profit and loss (local UK)'):
            actual_pl = self.formatted_report['financials']['statements'][0]
            self.assertEqual(actual_pl['statement_type'], 'PROFIT_AND_LOSS')
            self.assertEqual(actual_pl['statement_format'], 'LocalFinancialsCSUK')

            self.assert_entry_with(
                actual_pl['entries'][0],
                'exports',
                None,
                'operating_profit'
            )

            self.assert_entry_with(
                actual_pl['groups'][0],
                'turnover',
                None,
            )

            self.assert_entry_with(
                actual_pl['entries'][5],
                'depreciation',
                7953.0,
                'profit_before_tax',
                yoy=2.417705199828105
            )

        with self.subTest('returns balance sheet (local UK)'):
            actual_balance_sheet = self.formatted_report['financials']['statements'][1]
            self.assertEqual(actual_balance_sheet['statement_type'], 'BALANCE_SHEET')
            self.assertEqual(actual_balance_sheet['statement_format'], 'LocalFinancialsCSUK')

            self.assert_entry_with(
                actual_balance_sheet['entries'][0],
                'tangible_assets',
                27588.0,
                'total_fixed_assets',
                yoy=2.723579430422459
            )

            self.assert_entry_with(
                actual_balance_sheet['groups'][0],
                'total_fixed_assets',
                27588.0,
                yoy=2.723579430422459
            )

            self.assert_entry_with(
                actual_balance_sheet['entries'][11],
                'bank_overdraft_and_ltl',
                0.0,
                'total_long_term_liabilities',
            )

        with self.subTest('returns capital & reserves (local UK)'):
            actual_cap_sheet = self.formatted_report['financials']['statements'][2]
            self.assertEqual(actual_cap_sheet['statement_type'], 'CAPITAL_AND_RESERVES')
            self.assertEqual(actual_cap_sheet['statement_format'], 'LocalFinancialsCSUK')

            self.assert_entry_with(
                actual_cap_sheet['entries'][0],
                'issued_share_capital',
                138.0,
                'total_shareholders_equity',
                yoy=0.14049586776859505
            )

            self.assert_entry_with(
                actual_cap_sheet['groups'][0],
                'total_shareholders_equity',
                263198.0,
                yoy=0.6043180377432097
            )

            with self.subTest('handles yoy with negative numbers'):
                self.assert_entry_with(
                    actual_cap_sheet['entries'][2],
                    'revenue_reserves',
                    -1150078,
                    'total_shareholders_equity',
                    yoy=-1.3751146173227045
                )

        with self.subTest('returns other financial items (local UK)'):
            actual_other_financials = self.formatted_report['financials']['statements'][3]
            self.assertEqual(actual_other_financials['statement_type'], 'OTHER_FINANCIAL_ITEMS')
            self.assertEqual(actual_other_financials['statement_format'], 'LocalFinancialsCSUK')

            self.assertEqual(actual_other_financials['entries'], [])

            self.assert_entry_with(
                actual_other_financials['groups'][0],
                'net_worth',
                263198.0,
                yoy=0.6043180377432097
            )

        with self.subTest('returns cash flow'):
            actual_cash_flow = self.formatted_report['financials']['statements'][4]
            self.assertEqual(actual_cash_flow['statement_type'], 'CASH_FLOW')
            self.assertEqual(actual_cash_flow['statement_format'], 'LocalFinancialsCSUK')

            self.assertEqual(actual_cash_flow['entries'], [])

            self.assert_entry_with(
                actual_cash_flow['groups'][0],
                'net_cash_flow_from_operations',
                None
            )

        with self.subTest('returns profit and loss (global)'):
            actual_pl = self.formatted_report['financials']['statements'][15]
            self.assertEqual(actual_pl['statement_type'], 'PROFIT_AND_LOSS')
            self.assertEqual(actual_pl['statement_format'], 'GlobalFinancialsGGS')

            self.assert_entry_with(
                actual_pl['entries'][0],
                'operating_costs',
                None,
                'operating_profit'
            )

            self.assert_entry_with(
                actual_pl['groups'][0],
                'revenue',
                None,
            )

            self.assert_entry_with(
                actual_pl['entries'][7],
                'depreciation',
                7953.0,
                'profit_before_tax',
                yoy=2.417705199828105
            )

        with self.subTest('returns balance sheet (global)'):
            actual_balance_sheet = self.formatted_report['financials']['statements'][15+1]
            self.assertEqual(actual_balance_sheet['statement_type'], 'BALANCE_SHEET')
            self.assertEqual(actual_balance_sheet['statement_format'], 'GlobalFinancialsGGS')

            self.assert_entry_with(
                actual_balance_sheet['entries'][0],
                'trade_receivables',
                31764.0,
                'total_receivables',
                yoy=0.05922368947579031
            )

            self.assert_entry_with(
                actual_balance_sheet['groups'][0],
                'cash',
                244244.0,
                yoy=0.62977099236641229
            )

        with self.subTest('returns capital & reserves (global)'):
            actual_cap_sheet = self.formatted_report['financials']['statements'][15+2]
            self.assertEqual(actual_cap_sheet['statement_type'], 'CAPITAL_AND_RESERVES')
            self.assertEqual(actual_cap_sheet['statement_format'], 'GlobalFinancialsGGS')

            self.assert_entry_with(
                actual_cap_sheet['entries'][0],
                'called_up_share_capital',
                138.0,
                'total_shareholders_equity',
                yoy=0.14049586776859505
            )

            self.assert_entry_with(
                actual_cap_sheet['groups'][0],
                'total_shareholders_equity',
                263198.0,
                yoy=0.6043180377432097
            )

            with self.subTest('handles yoy with negative numbers'):
                self.assert_entry_with(
                    actual_cap_sheet['entries'][2],
                    'revenue_reserves',
                    -1150078,
                    'total_shareholders_equity',
                    yoy=-1.3751146173227045
                )

        with self.subTest('returns other financial items (global)'):
            actual_other_financials = self.formatted_report['financials']['statements'][15+3]
            self.assertEqual(actual_other_financials['statement_type'], 'OTHER_FINANCIAL_ITEMS')
            self.assertEqual(actual_other_financials['statement_format'], 'GlobalFinancialsGGS')

            self.assertEqual(actual_other_financials['entries'], [])

            self.assert_entry_with(
                actual_other_financials['groups'][0],
                'net_worth',
                263198.0,
                yoy=0.6043180377432097
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

    def test_merges_and_processes_unknown_director_with_company_psc_and_shareholder(self):
        self.unknown_officer_deduplicator.add_shareholders(
            [
                CreditsafeSingleShareholder({
                    'name': 'some star',
                    'entity_type': 'COMPANY'
                })
            ]
        )
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

        self.assertIsNotNone(associates[0].shareholder)
        self.assertIsNotNone(associates[0].officer)
        self.assertIsNotNone(associates[0].psc)
        self.assertEqual(associates[0].entity_type, 'COMPANY')

        associate = process_associate_data(associates[0], 'GBR', None)
        self.assertEqual(associate.entity_type, 'COMPANY')


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
                    'date': '2011-03-29 00:00:00',
                    'credit_limit': {'value': 0.0}
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

    def test_handles_missing_credit_and_limit_history(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'creditScore': {
                'currentCreditRating': {
                    'commonValue': 'A',
                    'providerValue': {
                        'value': '75'
                    },
                    'providerDescription': 'Good value',
                    'creditLimit': {
                        'value': '1500.0'
                    }
                },
                'previousCreditRating': {
                    'commonValue': 'B'
                },
                'latestRatingChangeDate': '2011-03-29 00:00:00'
            },
        })

        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [{
                    'date': '2011-03-29 00:00:00',
                    'international_rating': {'value': 'A'},
                    'credit_rating': {'value': '75', 'description': 'Good value'},
                    'credit_limit': {'value': 1500.0}
                }]
            }
        )

    def test_handles_bad_credit_limit_and_does_not_return_it(self):
        report = CreditSafeCompanyReport.from_json({
            **self.base_metadata,
            'creditScore': {
                'currentCreditRating': {
                    'commonValue': 'A',
                    'creditLimit': {
                        'value': 'text'
                    }
                },
                'latestRatingChangeDate': '2011-03-29 00:00:00'
            },
        })

        self.assertDictEqual(
            Financials(report.to_financials()).serialize(),
            {
                'credit_history': [{
                    'date': '2011-03-29 00:00:00',
                    'international_rating': {'value': 'A'}
                }]
            }
        )

    def test_filters_consolidated_accounts(self):
        """
        Creditsafe sometimes sends reports that are "consolidated", alongside non consolidated ones.
        And for some companies, only consolidated ones.
        Accountants usually use the non consolidated ones.
        Make sure we only send one type of report, and don't mix them on the same profile
        """
        def get_test_data(local_consolidated, global_consolidated):
            return {
                "localFinancialStatements": [
                    {
                        "type": "LocalFinancialsCSUK",
                        "yearEndDate": "2017-12-31T00:00:00Z",
                        "numberOfWeeks": 52,
                        "currency": "GBP",
                        "consolidatedAccounts": local_consolidated,
                        "auditQualification": "The company is exempt from audit",
                        "profitAndLoss": {
                            "depreciation": 7953.0,
                            "auditFees": 0.0
                        }
                    }
                ],
                "financialStatements": [
                    {
                        "type": "GlobalFinancialsGGS",
                        "yearEndDate": "2017-12-31T00:00:00Z",
                        "numberOfWeeks": 52,
                        "currency": "GBP",
                        "consolidatedAccounts": global_consolidated,
                        "profitAndLoss": {
                            "depreciation": 7953.0,
                            "amortisation": 0.0,
                            "otherAppropriations": 0.0
                        }
                    }
                ]
            }

        for local_v, global_v, expected_number \
                in [
                    (False, False, 9), (True, True, 9), (False, True, 5), (True, False, 4),
                    (None, False, 9), (None, None, 9), (False, None, 9), (None, True, 5), (True, None, 4)]:
            report = Financials(
                CreditSafeCompanyReport.from_json({
                    **self.base_metadata,
                    **get_test_data(local_v, global_v)
                }).to_financials()
            ).serialize()
            # Returns expected number of statements, ignoring consolidated accounts if both are present
            self.assertEqual(len(report.get("statements", [])), expected_number, f"case {local_v}, {global_v}")

    def test_handles_conflicting_consolidated_values(self):
        report = Financials(
            CreditSafeCompanyReport.from_json({
                **self.base_metadata,
                **{
                    "localFinancialStatements": [
                        {
                            "type": "LocalFinancialsCSUK",
                            "yearEndDate": "2017-12-31T00:00:00Z",
                            "numberOfWeeks": 52,
                            "currency": "GBP",
                            "consolidatedAccounts": True,
                            "auditQualification": "The company is exempt from audit",
                            "profitAndLoss": {
                                "depreciation": 7953.0,
                                "auditFees": 0.0
                            }
                        },
                        {
                            "type": "LocalFinancialsCSUK",
                            "yearEndDate": "2017-12-31T00:00:00Z",
                            "numberOfWeeks": 52,
                            "currency": "GBP",
                            "consolidatedAccounts": False,
                            "auditQualification": "The company is exempt from audit",
                            "profitAndLoss": {
                                "depreciation": 1000.0,
                                "auditFees": 0.0
                            }
                        }
                    ]
                }
            }).to_financials()
        ).serialize()
        # Returns a set of statements (not doubling it)
        self.assertEqual(len(report.get("statements", [])), 5)

        # Picks up the non consolidated ones by default
        self.assertEqual(report['statements'][0]['entries'][5]['value']['value'], 1000)
        self.assertEqual(report['statements'][0]['entries'][5]['name'], 'depreciation')

    def test_handles_known_bad_scope(self):
        other_ggs_type = "GGS Standardised"
        report = Financials(
            CreditSafeCompanyReport.from_json({
                **self.base_metadata,
                **{
                    "financialStatements": [
                        {
                            "type": other_ggs_type,
                            "yearEndDate": "2017-12-31T00:00:00Z",
                            "numberOfWeeks": 52,
                            "currency": "GBP",
                            "consolidatedAccounts": True,
                            "auditQualification": "The company is exempt from audit",
                        }
                    ]
                }
            }).to_financials()
        ).serialize()
        # Returns a set of global statements
        self.assertEqual(len(report.get("statements", [])), 4)


class TestYoy(unittest.TestCase):

    @classmethod
    def create_statement(cls, date, value_1, value_2):
        r = Statement().import_data({
            'currency_code': 'GBP',
            'statement_format': 'LocalFinancialsCSUK',
            'date': date,
            'entries': [
                {
                    'group_name': 'profit_before_tax',
                    'name': 'depreciation',
                    'value': {
                        'currency_code': 'GBP',
                        'value': value_1,
                    },
                    'value_type': 'CURRENCY'
                },
                {
                    'group_name': 'profit_before_tax',
                    'name': 'audit_fees',
                    'value': {
                        'currency_code': 'GBP',
                        'value': value_2,
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
                    'name': 'profit_before_tax',
                    'value': {
                        'currency_code': 'GBP',
                        'value': value_1 + value_2 if value_1 is not None and value_2 is not None else None,
                    },
                    'value_type': 'CURRENCY'
                }
            ],
            'statement_type': 'PROFIT_AND_LOSS'
        }, apply_defaults=True)
        r.validate()
        return r

    def test_yoy_is_present(self):
        statements = [
            self.create_statement('2019-12-31T00:00:00Z', 20, 4),
            self.create_statement('2018-12-31T00:00:00Z', 16, 4),
            self.create_statement('2017-12-31T00:00:00Z', 20, 4),
        ]
        with_yoy(statements)

        result = [s.serialize() for s in statements]
        self.assertEqual(result[0]['entries'][0]['yoy'], 0.25)
        self.assertEqual(result[0]['entries'][1]['yoy'], 0.0)
        self.assertEqual(result[0]['groups'][1]['yoy'], 0.2)

        self.assertEqual(result[1]['entries'][0]['yoy'], -0.2)
        self.assertEqual(result[1]['entries'][1]['yoy'], 0.0)
        self.assertEqual(result[1]['groups'][1]['yoy'], -0.16666666666666666)

        self.assertNotIn('yoy', result[2]['entries'][0])
        self.assertNotIn('yoy', result[2]['entries'][1])
        self.assertNotIn('yoy', result[2]['groups'][1])

    def test_yoy_if_current_value_0(self):
        statements = [
            self.create_statement('2019-12-31T00:00:00Z', 0, 0),  # crt value 0
            self.create_statement('2018-12-31T00:00:00Z', 1, None),
        ]
        with_yoy(statements)

        result = [s.serialize() for s in statements]
        self.assertEqual(result[0]['entries'][0]['yoy'], -1.0)
        self.assertNotIn('yoy', result[0]['entries'][1])

    def test_no_yoy_if_no_value(self):
        statements = [
            self.create_statement('2019-12-31T00:00:00Z', 0, None),  # crt value None
            self.create_statement('2018-12-31T00:00:00Z', None, 3),  # prev value none
        ]
        with_yoy(statements)

        result = [s.serialize() for s in statements]
        self.assertNotIn('yoy', result[0]['entries'][0])
        self.assertNotIn('yoy', result[0]['entries'][1])
        self.assertNotIn('yoy', result[0]['groups'][0])
        self.assertNotIn('yoy', result[0]['groups'][1])

    def test_no_yoy_if_previous_value_0(self):
        statements = [
            self.create_statement('2019-12-31T00:00:00Z', 1, None),
            self.create_statement('2018-12-31T00:00:00Z', 0, 0),  # prev value 0
        ]
        with_yoy(statements)

        result = [s.serialize() for s in statements]
        self.assertNotIn('yoy', result[0]['entries'][0])
        self.assertNotIn('yoy', result[0]['entries'][1])


class TestCreditSafeNotificationEventsResponse(unittest.TestCase):

    def test_from_json_no_data(self):
        res = CreditSafeNotificationEventsResponse.from_json({
            'total_count': 0,
            'data': [],
            'paging': {
                'size': 10,
                'prev': None,
                'next': None,
                'last': 0
            }
        })

        self.assertIsInstance(res, CreditSafeNotificationEventsResponse)
        self.assertEqual(res.total_count, 0)
        self.assertEqual(len(res.data), 0)
        self.assertEqual(res.paging.size, 10)
        self.assertIsNone(res.paging.prev)
        self.assertIsNone(res.paging.next)
        self.assertEqual(res.paging.last, 0)

    def test_from_json_with_data(self):
        res = CreditSafeNotificationEventsResponse.from_json({
            "totalCount": 36,
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
                    "eventDate": (datetime.now() - timedelta(seconds=1)).isoformat(),
                    "newValue": "1600 AMPHITHEATRE PARKWAY, MOUNTAIN VIEW, CA, 94043-1351",
                    "oldValue": "1604 AMPHITHEATRE PARKWAY, MOUNTAIN VIEW, CA, 94043-1351",
                    "notificationEventId": randint(1, 9999999999),
                    "ruleCode": 105,
                    "ruleName": "Address"
                }
                for _ in range(10)
            ],
            "paging": {
                "size": 10,
                "prev": 0,
                "next": 2,
                "last": 3
            }
        })

        self.assertIsInstance(res, CreditSafeNotificationEventsResponse)
        self.assertEqual(res.total_count, 36)
        self.assertEqual(len(res.data), 10)
        self.assertEqual(res.paging.size, 10)
        self.assertEqual(res.paging.prev, 0)
        self.assertEqual(res.paging.next, 2)
        self.assertEqual(res.paging.last, 3)

    def test_to_passfort_format_with_company_data_events(self):
        event = CreditSafeNotificationEvent({
            "company": {
                "id": "GB-0-03375464",
                "safeNumber": "UK03033453",
                "name": "THE DURHAM BREWERY LIMITED",
                "countryCode": "GB",
                "portfolioId": 1017586,
                "portfolioName": "Durham Brewery"
            },
            "eventId": 512812323,
            "eventDate": "2020-02-28T05:33:02",
            "createdDate": "2020-02-29T00:16:47",
            "notificationEventId": 81051991,
            "ruleCode": 2202,
            "ruleName": "Company Status"
        })

        response = CreditSafeNotificationEvent.to_passfort_format(event)

        self.assertEqual(
            response,
            MonitoringEvent({
                'creditsafe_id': 'GB-0-03375464',
                'event_type': MonitoringConfigType.VERIFY_COMPANY_DETAILS.value,
                'event_date': '2020-02-28T05:33:02',
                'rule_code': 2202
            })
        )

    def test_to_passfort_format_with_financial_events(self):
        event = CreditSafeNotificationEvent({
            "company": {
                "id": "GB-0-03375464",
                "safeNumber": "UK03033453",
                "name": "THE DURHAM BREWERY LIMITED",
                "countryCode": "GB",
                "portfolioId": 1017586,
                "portfolioName": "Durham Brewery"
            },
            "eventId": 512812323,
            "eventDate": "2020-02-28T05:33:02",
            "newValue": "33",
            "oldValue": "51",
            "createdDate": "2020-02-29T00:16:47",
            "notificationEventId": 81051991,
            "ruleCode": 101,
            "ruleName": "International Rating  |Reduce by {0} Band(s) OR Less than Band {1}"
        })

        response = CreditSafeNotificationEvent.to_passfort_format(event)

        self.assertEqual(
            response,
            MonitoringEvent({
                'creditsafe_id': 'GB-0-03375464',
                'event_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA.value,
                'event_date': '2020-02-28T05:33:02',
                'rule_code': 101
            })
        )

    def test_to_passfort_format_with_global_financial_events(self):
        event = CreditSafeNotificationEvent({
            "company": {
                "id": "GB-0-03375464",
                "safeNumber": "UK03033453",
                "name": "THE DURHAM BREWERY LIMITED",
                "countryCode": "GB",
                "portfolioId": 1017586,
                "portfolioName": "Durham Brewery"
            },
            "eventId": 512812323,
            "eventDate": "2020-02-28T05:33:02",
            "createdDate": "2020-02-29T00:16:47",
            "notificationEventId": 81051991,
            "ruleCode": 802,
            "ruleName": "Share captial"
        })

        response = CreditSafeNotificationEvent.to_passfort_format(event)

        self.assertEqual(
            response,
            MonitoringEvent({
                'creditsafe_id': 'GB-0-03375464',
                'event_type': MonitoringConfigType.ASSESS_FINANCIAL_DATA.value,
                'event_date': '2020-02-28T05:33:02',
                'rule_code': 802
            })
        )

    def test_to_passfort_format_with_unknown_event(self):
        event = CreditSafeNotificationEvent({
            "company": {
                "id": "GB-0-03375464",
                "safeNumber": "UK03033453",
                "name": "THE DURHAM BREWERY LIMITED",
                "countryCode": "GB",
                "portfolioId": 1017586,
                "portfolioName": "Durham Brewery"
            },
            "eventId": 512812323,
            "eventDate": "2020-02-28T05:33:02",
            "createdDate": "2020-02-29T00:16:47",
            "notificationEventId": 81051991,
            "ruleCode": 1024545687,
            "ruleName": "Share captial"
        })

        response = CreditSafeNotificationEvent.to_passfort_format(event)

        self.assertIsNone(response)

