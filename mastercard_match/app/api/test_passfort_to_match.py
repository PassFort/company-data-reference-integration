from unittest import TestCase
from os import path
from json import loads
from .match import TerminationInquiryRequest, Principal, Merchant
from .passfort import InquiryRequest, MatchConfig, MatchCredentials, CompanyData


def read_test_data(name):
    with open(path.join(path.dirname(__file__), name)) as file:
        return file.read()


company_with_associates_json = loads(read_test_data('company_with_associate.json'))


class TestPassfortToMatch(TestCase):
    company_data = CompanyData().import_data(company_with_associates_json, apply_defaults=True)
    merchant = Merchant().from_passfort(company_data)

    def test_parses_associates(self):
        self.maxDiff = None
        self.assertListEqual(self.merchant.to_primitive()['Principal'], [{
            'FirstName': 'Sam',
            'MiddleInitial': 'P',
            'LastName': 'Bridges',
            'NationalId': 'QQ123456C',
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
