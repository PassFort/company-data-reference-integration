from unittest import TestCase
from passfort.individual_data import IndividualData
from passfort.company_data import CompanyData
from passfort.cifas_check import CifasConfig
from cifas.search import FullSearchRequest 
from tests import INDIVIDUAL_DATA_FULL, INDIVIDUAL_DATA_MINIMAL, COMPANY_DATA_FULL, COMPANY_DATA_MINIMAL


class TestPassfortToCifas(TestCase):
    @property
    def cifas_config(self):
        return CifasConfig(
            product_code='PXX',
            search_type='XX',
            requesting_institution=98293892,
            use_uat=False,
        )

    def assert_config_on_request(self, request):
        config = self.cifas_config
        self.assertEqual(config.product_code, request.Product)
        self.assertEqual(config.search_type, request.SearchType)

    def assert_personal_details(self, individual_data, request):
        personal_details = individual_data.personal_details

        self.assertEqual(
            personal_details.name.family_name, 
            request.Party.Surname,
        )

        self.assertEqual(
            personal_details.name.given_names[0], 
            request.Party.FirstName,
        )

        if personal_details.dob:
            self.assertEqual(
                personal_details.dob.value, 
                request.Party.BirthDate,
            )

        self.assertIsNotNone(request.Party.Address)

    def assert_contact_details(self, individual_data, request):
        contact_details = individual_data.contact_details

        self.assertEqual(
            contact_details.email, 
            request.Party.EmailAddress,
        )

        self.assertEqual(
            contact_details.phone_number, 
            request.Party.HomeTelephone,
        )

    def assert_national_id_number(self, individual_data, request):
        personal_details = individual_data.personal_details
        self.assertEqual(request.Party.NationalInsuranceNumber, personal_details.national_identity_number['GBR'])

    def assert_bank_accounts(self, individual_data, request):
        bank_accounts = individual_data.banking_details.bank_accounts
        for bank_account in bank_accounts:
            self.assertIsNotNone(next((
                finance_details for finance_details in (request.Party.Finance or [])
                if finance_details.BankAccount.SortCode == bank_account.sort_code and
                finance_details.BankAccount.AccountNumber == bank_account.account_number
            ), None), f'Could not find bank account: {bank_account}')

    def assert_company_required_metadata(self, company_data, request):
        metadata = company_data.metadata

        self.assertEqual(
            metadata.name,
            request.Party.CompanyName,
        )

        self.assertEqual(
            metadata.number,
            request.Party.CompanyNumber,
        )

        self.assertIsNotNone(request.Party.Address)

    def assert_company_contact_details(self, company_data, request):
        contact_details = company_data.metadata.contact_details

        self.assertEqual(
            contact_details.email, 
            request.Party.EmailAddress,
        )

        self.assertEqual(
            contact_details.phone_number, 
            request.Party.CompanyTelephone,
        )

    def test_full_individual_party(self):
        individual_data = IndividualData.from_dict(INDIVIDUAL_DATA_FULL)
        search_request = FullSearchRequest.from_passfort_data(individual_data, self.cifas_config)
        self.assert_config_on_request(search_request)
        self.assert_personal_details(individual_data, search_request)
        self.assert_contact_details(individual_data, search_request)
        self.assert_national_id_number(individual_data, search_request)
        self.assert_bank_accounts(individual_data, search_request)

    def test_minimal_individual_party(self):
        individual_data = IndividualData.from_dict(INDIVIDUAL_DATA_MINIMAL)
        search_request = FullSearchRequest.from_passfort_data(individual_data, self.cifas_config)
        self.assert_config_on_request(search_request)
        self.assert_personal_details(individual_data, search_request)

    def test_full_company_party(self):
        company_data = CompanyData.from_dict(COMPANY_DATA_FULL)
        search_request = FullSearchRequest.from_passfort_data(company_data, self.cifas_config)
        self.assert_config_on_request(search_request)
        self.assert_company_required_metadata(company_data, search_request)
        self.assert_company_contact_details(company_data, search_request)

    def test_minimal_company_party(self):
        company_data = CompanyData.from_dict(COMPANY_DATA_MINIMAL)
        search_request = FullSearchRequest.from_passfort_data(company_data, self.cifas_config)
        self.assert_config_on_request(search_request)
        self.assert_company_required_metadata(company_data, search_request)
