from enum import Enum, unique
from typing import List, Optional
import logging

from flask import abort, request
from schematics import Model
from schematics.common import NOT_NONE
from schematics.exceptions import DataError, ValidationError
from schematics.types import DateType, IntType, ListType, ModelType, StringType
from schematics.types.base import TypeMeta
from fuzzywuzzy import fuzz

from .passfort import CompanyData, InquiryRequest, MatchConfig, CollectedData


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


termination_reason_mapping = {
    "00": "Questionable Merchant/Under Investigation",
    "01": "Account Data Compromise",
    "02": "Common Point of Purchase",
    "03": "Laundering",
    "04": "Excessive Chargebacks",
    "05": "Excessive Fraud",
    #  "06": "Reserved for Future Use",
    "07": "Fraud Conviction",
    "08": "MasterCard Questionable Merchant Audit Program",
    "09": "Bankruptcy/Liquidation/Insolvency",
    "10": "Violation of MasterCard Standards",
    "11": "Merchant collusion",
    "12": "PCI Data Security Standard, Noncompliance",
    "13": "Illegal Transactions",
    "14": "Identity Theft",
    # mastercard specific termination codes
    "20": "Questionable Merchant Audit Program",
    "21": "Questionable Merchant Audit Program",
    "22": "Excessive Chargeback Merchant",
    "23": "Merchant Collusion",
    "24": "Illegal Transaction",
}

termination_reason_description_mapping = {
    "00": "A merchant that is the subject of an audit with respect to Standards. Mastercard currently conducts" +
           "special Merchant audits for excessive fraud-to-sales ratios, excessive chargebacks, or counterfeit activity.",
    "01": "An occurrence that results, directly or indirectly, in the unauthorized access to ordisclosure of Account data",
    "02": "Account data is stolen at the Merchant and then used for fraudulent purchases at other Merchant locations.",
    "03": "The merchant was engaged in laundering activity. Laundering means that a merchant presented to its acquirer" +
          "transaction records that were not valid transactions for sales of goods or services between that merchant and a bona fide cardholder.",
    "04": "With respect to a Merchant reported by a Mastercard Acquirer, the number of chargebacks in any single month" +
          "exceeded 1% of its Mastercard sales transactions inthat month, and those chargebacks totaled USD 5,000 or more." +
          "With respect to a merchant reported by an American Express® acquirer (ICA numbers 102 through 125), the merchant" +
          "exceeded the chargeback thresholds of American Express, as determined by American Express.",
    "05": "The merchant affected fraudulent transactions of any type (counterfeit or otherwise) meeting or exceeding the" +
          "following minimum reporting standard: the merchant’s fraud-to-sales dollar volume ratio was 8% or greater in a" +
          "calendar month, and the merchant affected ten or more fraudulent transactions totaling USD 5,000 or more in that calendar month.",
    #  "06": "Reserved",
    "07": "There was a criminal fraud conviction of a principal owner or partner of the merchant",
    "08": "The merchant was determined to be a Questionable Merchant as per the criteria setforth in the Mastercard" +
          "Questionable Merchant Audit Program (refer to section 8.4 ofthe Security Rules and Procedures manual.",
    "09": "The merchant was unable or is likely to become unable to discharge its financial obligations.",
    "10": "With respect to a merchant reported by a Mastercard Acquirer, the merchant was inviolation of one or more" +
          "Mastercard Standards that describe procedures to be employe dby the merchant in Transactions in which Mastercard" +
          "cards are used, including by way of example and not limitation the Standards for honoring all Cards, displaying the" +
          "Marks,charges to Cardholders, minimum/maximum Transaction amount restrictions, and prohibited Transactions set forth" +
          "in the Mastercard Rules manual: With respect to a merchant reported by an American Express acquirer (ICA numbers 102" +
          "through 125), the merchant was in violation of one or more American Express bylaws, rules operating regulations, and" +
          "policies that set forth procedures to be employed by the merchant in transactions in which American Express cards are used.",
    "11": "The merchant participated in fraudulent collusive activity.",
    "12": "The merchant failed to comply with Payment Card Industry (PCI) Data Security Standard requirements.",
    "13": "The merchant was engaged in illegal transactions",
    "14": "The acquirer has reason to believe that the identity of the listed merchant or its principal owners" +
          "was unlawfully assumed for the purpose of unlawfully entering into a merchant agreement.",
    "20": "Merchant that Mastercard has determined to be a Questionable Merchant as per thecriteria set" +
          "forth in the Mastercard Questionable Merchant Audit Program (refer tosection 8.4 of this manual).",
    "21": "A non-face-to-face adult content and services Merchant that Mastercard has determined to have violated Mastercard excessive chargeback Standards.",
    "22": "A merchant that Mastercard has determined to have violated the Mastercard Excessive Chargeback Program and is not an Electronic Commerce Adult Content (Videotext) Special Merchant.",
    "23": "The merchant participated in fraudulent collusive activity, as determined by the acquirerby" +
          "any means, including data reporting, criminal conviction, law enforcement investigation, or as determined by Mastercard.",
    "24": "The merchant was engaged in illegal transactions",
}


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
    city = StringType(serialized_name='City', default=None)
    country = StringType(serialized_name='Country', default=None)
    country_sub_division = StringType(serialized_name='CountrySubdivision', default=None)
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
            address['CountrySubdivision'] = state
            address['PostalCode'] = passfort_address.get('PostalCode')
        return cls().import_data(address, apply_defaults=True)


class SearchCriteria(Model):
    search_all = StringType(choices=['N', 'Y'], default='Y', serialized_name='SearchAll')
    country = ListType(StringType(), serialized_name='Country', default=None)
    min_possible_match_count = IntType(serialized_name='MinPossibleMatchCount', default=3)
    region = ListType(StringType(), serialized_name='Region', default=None)

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, config: MatchConfig):
        if config.worldwide_search:
            search_all = 'Y'
        else:
            search_all = 'N'
        return cls().import_data({
            'search_all': search_all,
            'country': config.country_search,
            'min_possible_match_count': config.min_phonetic_matches,
            'region': config.region_search
        }, apply_defaults=True)


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
    def from_passfort(cls, individual_data: CollectedData, search_criteria: SearchCriteria):
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
            'address': Address().from_passfort(individual_data.current_address),
            'drivers_license': drivers_license,
            'phone_number': individual_data.contact_details.phone_number,
            'search_criteria': search_criteria,
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
    def from_passfort(cls, company_data: CompanyData, search_criteria=None):
        search_criteria = SearchCriteria().from_passfort(search_criteria) if search_criteria else SearchCriteria()
        principals = [
            InputPrincipal().from_passfort(p['collected_data'], search_criteria)
            for p in company_data.associated_entities
        ] or None
        return cls().import_data({
            'name': company_data.metadata.name,
            'address': Address().from_passfort(company_data.metadata.first_address),
            'principals': principals,
            'url': company_data.metadata.contact_details.url,
            'search_criteria': search_criteria

        }, apply_defaults=True)


class TerminationInquiryRequest(Model):
    acquirer_id: str = StringType(required=True, serialized_name='AcquirerId')
    merchant: InputMerchant = ModelType(InputMerchant, serialized_name='Merchant')

    @classmethod
    def from_passfort(cls, passfort_data: InquiryRequest):
        return cls().import_data({
            'AcquirerId': passfort_data.credentials.acquirer_id,
            'Merchant': InputMerchant.from_passfort(passfort_data.input_data, passfort_data.config),
        })

    def as_request_body(self):
        return {'TerminationInquiryRequest': self.to_primitive()}


class InquiredMerchant(Merchant):
    principals: List[Principal] = ListType(ModelType(Principal), serialized_name='Principal', min_size=1)
    merchant_match = ModelType(MerchantMatch, required=True, serialized_name='MerchantMatch')


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
    contact_details: List[ContactDetails] = ListType(ModelType(ContactDetails), default=[])

    def add_contact_details(self, raw_data):
        data = raw_data.get('ContactResponse', {})
        data = data.get('Contact', [])
        self.contact_details = [ContactDetails().import_data({
            'bank_name': c.get('BankName'),
            'region': c.get('Region'),
            'first_name': c.get('FirstName'),
            'last_name': c.get('LastName'),
            'phone_number': c.get('FaxNumber'),
            'email_address': c.get('EmailAddress'),
        }, apply_defaults=True) for c in data]


def from_match_inquiry_response(data):
    def unwrap_match(match):
        return {
            **match.get('Merchant'),
            'MerchantMatch': match.get('MerchantMatch'),
        }

    possible_merchant_matches = data.get('PossibleMerchantMatches', {})
    possible_inquiry_matches = data.get('PossibleInquiryMatches', {})

    possible_merchant_matches = (possible_merchant_matches[0] if possible_merchant_matches else {})
    possible_inquiry_matches = (possible_inquiry_matches[0] if possible_inquiry_matches else {})

    total_merchant_matches = possible_merchant_matches.get('TotalLength')
    total_inquiry_matches = possible_inquiry_matches.get('TotalLength')

    possible_merchant_matches = possible_merchant_matches.get('TerminatedMerchant', [])
    possible_inquiry_matches = possible_inquiry_matches.get('InquiredMerchant', [])

    possible_merchant_matches = [unwrap_match(m) for m in possible_merchant_matches]
    possible_inquiry_matches = [unwrap_match(m) for m in possible_inquiry_matches]

    return {
        'possible_merchant_matches': possible_merchant_matches,
        'possible_inquiry_matches': possible_inquiry_matches,
        'total_merchant_matches': total_merchant_matches,
        'total_inquiry_matches': total_inquiry_matches,
        'Ref': data.get('Ref')
    }


class RetroInquiryResults(Model):
    possible_merchant_matches: List[TerminatedMerchant] = ListType(ModelType(TerminatedMerchant), default=[])

    @classmethod
    def from_match_response(cls, data):
        data = from_match_inquiry_response(data.get('RetroInquiryResponse', {}))

        obj = cls().import_data({
            'possible_merchant_matches': data.get('possible_merchant_matches'),
        })
        obj.validate()

        return obj


class InquiryResults(Model):
    inquiry_reference = StringType(required=True)
    possible_merchant_matches: List[TerminatedMerchant] = ListType(ModelType(TerminatedMerchant), default=[])
    possible_inquiry_matches: List[InquiredMerchant] = ListType(ModelType(InquiredMerchant), default=[])
    total_merchant_matches = IntType(required=True)
    total_inquiry_matches = IntType(required=True)

    @property
    def ref(self):
        from urllib.parse import urlparse

        path = urlparse(self.inquiry_reference).path
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
        data = from_match_inquiry_response(data)

        obj = cls().import_data({
            'inquiry_reference': data.get('Ref'),
            'possible_merchant_matches': data.get('possible_merchant_matches'),
            'possible_inquiry_matches': data.get('possible_inquiry_matches'),
            'total_merchant_matches': data.get('total_merchant_matches'),
            'total_inquiry_matches': data.get('total_inquiry_matches'),
        }, apply_defaults=True)

        obj.validate()

        return obj
