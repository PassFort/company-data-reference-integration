from enum import Enum, unique
from typing import List, Optional

from flask import abort, request
from schematics import Model
from schematics.common import NOT_NONE
from schematics.exceptions import DataError, ValidationError
from schematics.types import DateType, IntType, ListType, ModelType, StringType
from schematics.types.base import TypeMeta

from .passfort import CompanyData, IndividualData, InquiryRequest


class EnumMeta(TypeMeta):
    def __new__(mcs, name, bases, attrs):
        attrs['choices'] = [v for k, v in attrs.items() if not k.startswith('_') and k.isupper()]
        return TypeMeta.__new__(mcs, name, bases, attrs)


class EnumType(StringType, metaclass=EnumMeta):
    def __init__(self, **kwargs):
        super(EnumType, self).__init__(choices=self.choices, **kwargs)


class MatchType(EnumType):
    '''
        M00 - no match
        M01 - exact possible match
        M02 - phonetic possible match
    '''
    M00 = 'M00'
    M01 = 'M01'
    M02 = 'M02'


class PrincipalMatch(Model):
    name = MatchType(serialized_name='Name')
    address = MatchType(serialized_name='Address')
    phone_number = MatchType(serialized_name='PhoneNumber')
    alt_phone_number = MatchType(serialized_name='AltPhoneNumber')
    national_id = MatchType(serialized_name='NationalId')
    drivers_license = MatchType(serialized_name='DriversLicense')
    profile_id = StringType()


class MerchantMatch(Model):
    name = MatchType(serialized_name='Name')
    doing_business_as_name = MatchType(serialized_name='DoingBusinessAsName')
    address = MatchType(serialized_name='Address')
    phone_number = MatchType(serialized_name='PhoneNumber')
    alt_phone_number = MatchType(serialized_name='AltPhoneNumber')
    country_sub_division_tax_id = MatchType(serialized_name='CountrySubDivisionTaxId')
    national_tax_id = MatchType(serialized_name='NationalTaxId')
    service_prov_legal = MatchType(serialized_name='ServiceProvLegal')
    service_prov_dba = MatchType(serialized_name='ServiceProvDBA')
    principal_matches = ListType(ModelType(PrincipalMatch), serialized_name='PrincipalMatch')


class Address(Model):
    city = StringType(serialized_name='City', default=None)
    country = StringType(serialized_name='Country', default=None)
    country_sub_division = StringType(serialized_name='CountrySubDivision', default=None)
    line1 = StringType(serialized_name='Line1', default=None)
    line2 = StringType(serialized_name='Line2', default=None)
    postal_code = StringType(serialized_name='PostalCode', default=None)

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, passfort_address):
        address = {}
        street_number = passfort_address.get('street_number')
        route = passfort_address.get('route')
        premise = passfort_address.get('premise')
        subpremise = passfort_address.get('subpremise')
        state = passfort_address.get('state')

        address['Line1'] = ' '.join([
            str(v) for v in [street_number, route, premise, subpremise] if v is not None
        ]).strip()
        address['City'] = passfort_address.get('postal_town', None) or passfort_address.get('locality')
        address['Country'] = passfort_address.get('country')

        if state:
            address['CountrySubDivision'] = state
            address['PostalCode'] = passfort_address.get('PostalCode')
        return cls().import_data(address, apply_defaults=True)


class SearchCriteria(Model):
    search_all = StringType(choices=['N', 'Y'], default='Y', serialized_name='SearchAll')
    country = ListType(StringType(), serialized_name='Country', default=None)
    min_possible_match_count = IntType(serialized_name='MinPossibleMatchCount', default=3)
    region = ListType(StringType(), serialized_name='Region', default=None)

    class Options:
        export_level = NOT_NONE


class DriversLicense(Model):
    number = StringType(serialized_name='Number')
    country = StringType(serialized_name='Country')
    country_sub_division = StringType(serialized_name='CountrySubdivision', default=None)

    class Options:
        export_level = NOT_NONE


class Principal(Model):
    first_name = StringType(required=True, serialized_name='FirstName')
    last_name = StringType(required=True, serialized_name='LastName')
    middle_initial = StringType(serialized_name='MiddleInitial', default=None)
    phone_number = StringType(serialized_name='PhoneNumber', default=None)
    national_id = StringType(serialized_name='NationalId', default=None)
    address: Address = ModelType(Address, serialized_name='Address')
    drivers_license: DriversLicense = ModelType(DriversLicense, serialized_name='DriversLicense', default=None)

    class Options:
        export_level = NOT_NONE


class InputPrincipal(Principal):
    search_criteria: SearchCriteria = ModelType(SearchCriteria, serialized_name='SearchCriteria', default={})

    @classmethod
    def from_passfort(cls, individual_data: IndividualData):
        drivers_license = ({
            'number': individual_data.drivers_license.number,
            'country': individual_data.drivers_license.country_code,
            'country_sub_division': individual_data.drivers_license.issuing_state,
        } if individual_data.drivers_license else None)

        return cls().import_data({
            'first_name': individual_data.personal_details.name.given_names[0],
            'last_name': individual_data.personal_details.name.family_name,
            'middle_initial': individual_data.personal_details.name.middle_initial,
            'national_id': individual_data.personal_details.national_id,
            'address': Address().from_passfort(individual_data.personal_details.current_address),
            'drivers_license': drivers_license,
        }, apply_defaults=True)


class Merchant(Model):
    name: str = StringType(required=True, serialized_name='Name')
    phone_number = StringType(serialized_name='PhoneNumber', default=None)
    address: Address = ModelType(Address, required=True, serialized_name='Address')
    url = StringType(default=None)

    class Options:
        export_level = NOT_NONE


class InputMerchant(Merchant):
    search_criteria: SearchCriteria = ModelType(SearchCriteria, serialized_name='SearchCriteria', default={})
    principals: List[InputPrincipal] = ListType(ModelType(InputPrincipal), serialized_name='Principal', min_size=1)

    @classmethod
    def from_passfort(cls, company_data: CompanyData):
        principals = [
            InputPrincipal().from_passfort(p) for p in company_data.associated_entities
        ] or None

        return cls().import_data({
            'name': company_data.metadata.name,
            'address': Address().from_passfort(company_data.metadata.first_address),
            'principals': principals,
            'url': company_data.metadata.contact_details.url,
        }, apply_defaults=True)


class TerminationInquiryRequest(Model):
    acquirer_id: str = StringType(required=True, serialized_name='AcquirerId')
    merchant: InputMerchant = ModelType(InputMerchant, serialized_name='Merchant')

    @classmethod
    def from_passfort(cls, passfort_data: InquiryRequest):
        return cls().import_data({
            'AcquirerId': passfort_data.config.acquirer_id,
            'Merchant': InputMerchant.from_passfort(passfort_data.input_data),
        })

    def as_request_body(self):
        return {'TerminationInquiryRequest': self.to_primitive()}


class InquiredMerchant(Merchant):
    added_on = DateType(required=True, serialized_name='AddedOnDate', formats=['%m/%d/%Y'])
    added_by_aquirer_id = StringType(required=True, serialized_name='AddedByAcquirerID')
    principals: List[Principal] = ListType(ModelType(Principal), serialized_name='Principal', min_size=1)


class ContactDetails(Model):
    bank_name = StringType(default=None)
    region = StringType(default=None)
    first_name = StringType(default=None)
    last_name = StringType(default=None)
    phone_number = StringType(default=None)
    fax_number = StringType(default=None)
    email_address = StringType(default=None)

    class Options:
        export_level = NOT_NONE


class TerminatedMerchant(Merchant):
    added_on = DateType(required=True, serialized_name='AddedOnDate', formats=['%m/%d/%Y'])
    termination_reason_code = StringType(required=True, serialized_name='TerminationReasonCode')
    added_by_aquirer_id = StringType(required=True, serialized_name='AddedByAcquirerID')
    principals: List[Principal] = ListType(ModelType(Principal), serialized_name='Principal', min_size=1)
    merchant_match = ModelType(MerchantMatch, required=True, serialized_name='MerchantMatch')
    contact_details: List[ContactDetails] = ListType(ModelType(ContactDetails))

    def add_contact_details(self, raw_data):
        data = raw_data.get('ContactResponse', {})
        data = data.get('Contact', [])
        self.contact_details = [ContactDetails.import_data({
            'bank_name': c.get('BankName'),
            'region': c.get('Region'),
            'first_name': c.get('FirstName'),
            'last_name': c.get('LastName'),
            'phone_number': c.get('FaxNumber'),
            'email_address': c.get('EmailAddress'),
        }, apply_defaults=True) for c in data]


class InquiryResults(Model):
    inquiry_reference = StringType(required=True)
    possible_merchant_matches: List[TerminatedMerchant] = ListType(ModelType(TerminatedMerchant), default=[])
    possible_inquiry_matches: List[InquiredMerchant] = ListType(ModelType(InquiredMerchant), default=[])
    total_merchant_matches = IntType(required=True)
    total_inquiry_matches = IntType(required=True)

    @staticmethod
    def parse_ref(ref_url):
        from urllib.parse import urlparse

        if not ref_url:
            return None
        path = urlparse(ref_url).path
        return path.split('/')[-1]

    def should_fetch_more(self):
        should = self.total_inquiry_matches > len(self.possible_inquiry_matches) or \
            self.total_merchant_matches > len(self.possible_merchant_matches)

        return should

    def merge_data(self, data):
        new_response = InquiryResults().from_match_response(data)
        new_response.validate()

        self.possible_merchant_matches.extend(new_response.possible_merchant_matches)
        self.possible_inquiry_matches.extend(new_response.possible_inquiry_matches)

    @classmethod
    def from_match_response(cls, data):
        data = data.get('TerminationInquiry', {})
        possible_merchant_matches = data.get('PossibleMerchantMatches', {})
        possible_inquiry_matches = data.get('PossibleInquiryMatches', {})

        possible_merchant_matches = (possible_merchant_matches[0] if possible_merchant_matches else {})
        possible_inquiry_matches = (possible_inquiry_matches[0] if possible_inquiry_matches else {})

        total_merchant_matches = possible_merchant_matches.get('TotalLength')
        total_inquiry_matches = possible_inquiry_matches.get('TotalLength')

        possible_merchant_matches = possible_merchant_matches.get('TerminatedMerchant', [])
        possible_inquiry_matches = possible_inquiry_matches.get('InquiredMerchant', [])

        def unwrap_match(match):
            return {
                **match.get('Merchant'),
                'MerchantMatch': match.get('MerchantMatch'),
            }

        possible_merchant_matches = [unwrap_match(m) for m in possible_merchant_matches]
        possible_inquiry_matches = [unwrap_match(m) for m in possible_inquiry_matches]

        obj = cls().import_data({
            'inquiry_reference': cls.parse_ref(data.get('Ref')),
            'possible_merchant_matches': possible_merchant_matches,
            'possible_inquiry_matches': possible_inquiry_matches,
            'total_merchant_matches': total_merchant_matches,
            'total_inquiry_matches': total_inquiry_matches,
        }, apply_defaults=True)

        obj.validate()

        return obj
