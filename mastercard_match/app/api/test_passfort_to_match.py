from json import loads
from os import path
from unittest import TestCase

from .match import InputMerchant, Principal, TerminationInquiryRequest
from .passfort import (CompanyData, InquiryRequest, MatchConfig,
                       MatchCredentials)


def read_test_data(name):
    with open(path.join(path.dirname(__file__), name)) as file:
        return file.read()


company_with_associates_json = loads(read_test_data('company_with_associate.json'))


class TestPassfortToMatch(TestCase):
    company_data = CompanyData().import_data(company_with_associates_json, apply_defaults=True)
    merchant = InputMerchant().from_passfort(company_data, MatchConfig())

    def test_parses_associates(self):
        self.assertListEqual(self.merchant.to_primitive()['Principal'], [{
            'FirstName': 'Sam',
            'MiddleInitial': 'P',
            'LastName': 'Bridges',
            'NationalId': 'QQ123456C',
            "PhoneNumber": "+446240211322",
            'Address': {
                'City': 'London',
                'Country': 'GBR',
                'Line1': '11 Princelet Street Passfort Ltd'
            },
            'SearchCriteria': {
                'SearchAll': 'Y',
                'MinPossibleMatchCount': 3
            },
            'DriversLicense': {
                'Country': 'GBR',
                'Number': '1163265'
            },
        }])

    def test_parses_company(self):
        self.assertEqual(self.merchant.name, 'Goyette Group')
        self.assertDictEqual(self.merchant.address.to_primitive(), {
            'City': 'London',
            'Country': 'GBR',
            'Line1': '11 Princelet Street Passfort Ltd'
        })
        self.assertDictEqual(self.merchant.search_criteria.to_primitive(), {
            'SearchAll': 'Y',
            'MinPossibleMatchCount': 3,
        })
