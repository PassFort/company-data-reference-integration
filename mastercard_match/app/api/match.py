from schematics.exceptions import DataError, ValidationError
from enum import unique, Enum
from flask import abort, request
from schematics import Model
from schematics.types import ModelType, StringType, ListType, IntType, DateType
from schematics.types.base import TypeMeta
from typing import List, Optional
from .passfort import IndividualData, CompanyData, InquiryRequest
from schematics.common import NOT_NONE


class EnumMeta(TypeMeta):
    def __new__(mcs, name, bases, attrs):
        attrs['choices'] = [v for k, v in attrs.items() if not k.startswith('_') and k.isupper()]
        return TypeMeta.__new__(mcs, name, bases, attrs)


class EnumType(StringType, metaclass=EnumMeta):
    def __init__(self, **kwargs):
        super(EnumType, self).__init__(choices=self.choices, **kwargs)


class MatchType(EnumType):
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
    city = StringType(serialized_name='City', required=True)
    country = StringType(serialized_name='Country', required=True)
    country_sub_division = StringType(serialized_name='CountrySubDivision', default=None)
    line1 = StringType(serialized_name='Line1', required=True)
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

        address['Line1'] = ' '.join(
            [str(v) for v in [street_number, route, premise, subpremise] if v is not None]
        ).strip()
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
    number = StringType(required=True, serialized_name="Number")
    country = StringType(required=True, serialized_name="Country")
    country_sub_division = StringType(serialized_name="CountrySubdivision", default=None)

    class Options:
        export_level = NOT_NONE


class Principal(Model):
    first_name = StringType(required=True, serialized_name='FirstName')
    last_name = StringType(required=True, serialized_name='LastName')
    middle_initial = StringType(serialized_name='MiddleInitial')
    phone_number = StringType(serialized_name='PhoneNumber')
    national_id = StringType(serialized_name='NationalId')
    address: Address = ModelType(Address, serialized_name='Address')
    search_criteria: SearchCriteria = ModelType(SearchCriteria, serialized_name="SearchCriteria", default={})
    drivers_license: DriversLicense = ModelType(DriversLicense, serialized_name="DriversLicense")

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, individual_data: IndividualData):
        drivers_license = {
            "number": individual_data.drivers_license.number,
            "country": individual_data.drivers_license.country_code,
            "country_sub_division": individual_data.drivers_license.issuing_state
        } if individual_data.drivers_license else None

        return cls().import_data({
            "first_name": individual_data.personal_details.name.given_names[0],
            "last_name": individual_data.personal_details.name.family_name,
            "middle_initial": individual_data.personal_details.name.middle_initial,
            "national_id": individual_data.personal_details.national_id,
            "address": Address().from_passfort(individual_data.personal_details.current_address),
            "drivers_license": drivers_license,
        }, apply_defaults=True)


class Merchant(Model):
    name: str = StringType(required=True, serialized_name="Name")
    phone_number = StringType(serialized_name="PhoneNumber")
    address: Address = ModelType(Address, required=True, serialized_name="Address")
    principals: List[Principal] = ListType(
        ModelType(Principal), serialized_name='Principal', min_size=1
    )
    url = StringType(default=None)
    search_criteria: SearchCriteria = ModelType(SearchCriteria, serialized_name='SearchCriteria', default={})

    class Options():
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, company_data: CompanyData):
        principals = [Principal().from_passfort(p) for p in company_data.associated_entities] or None
        return cls().import_data({
            "name": company_data.metadata.name,
            "address": Address().from_passfort(company_data.metadata.first_address),
            "principals": principals,
            "url": company_data.metadata.contact_details.url,
        }, apply_defaults=True)


class TerminatedMerchant(Merchant):
    added_on = DateType(required=True, serialized_name="AddedOn")
    termination_reason_code = StringType(required=True, serialized_name="TerminationReasonCode")
    added_by_aquirer_id = StringType(required=True, serialized_name="AddedByAcquirerID")
    merchant_match = ModelType(MerchantMatch, required=True, serialized_name="MerchantMatch")


class InquiredMerchant(Merchant):
    added_on = DateType(required=True, serialized_name="AddedOn")
    added_by_aquirer_id = StringType(required=True, serialized_name="AddedByAcquirerID")


class PossibleMerchantMatches(Model):
    total_length = IntType(serialized_name="TotalLength")
    terminated_merchant: List[TerminatedMerchant] = ListType(
        ModelType(TerminatedMerchant), serialized_name="TerminatedMerchant"
    )


class PossibleInquiryMatches(Model):
    total_length = IntType(serialized_name="TotalLength")
    inquired_merchant: List[InquiredMerchant] = ListType(
        ModelType(PossibleMerchantMatches), serialized_name="InquiredMerchant"
    )


class TerminationInquiryRequest(Model):
    acquirer_id: str = StringType(required=True, serialized_name="AcquirerId")
    merchant: Merchant = ModelType(Merchant, serialized_name='Merchant')

    @classmethod
    def from_passfort(cls, passfort_data: InquiryRequest):
        return cls().import_data({
            "AcquirerId": passfort_data.config.acquirer_id,
            "Merchant": Merchant.from_passfort(passfort_data.input_data)
        }, apply_defaults=True)

    def as_request_body(self):
        return {
            "TerminationInquiryRequest": self.to_primitive()
        }


class TerminationInquiryResponse(Model):
    page_offset = IntType(required=True, serialized_name="PageOffset")
    transaction_ref_number = StringType(serialized_name="TransactionReferenceNumber")
    match_reference_url = StringType(required=True, serialized_name="Ref")
    possible_merchant_matches = ListType(ModelType(PossibleMerchantMatches), serialized_name="PossibleMerchantMatches")
    possible_inquiry_matches = ListType(ModelType(PossibleInquiryMatches), serialized_name="PossibleInquiryMatches")

    @property
    def match_reference(self):
        from urllib.parse import parse
        path = parse(self.match_reference_url).path

        return path.split('/')[-1]
