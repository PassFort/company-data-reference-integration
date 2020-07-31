from datetime import datetime
import pycountry
import re
import uuid
import nameparser
import concurrent.futures
from itertools import zip_longest, chain

from collections import defaultdict
from typing import Dict, Optional, Set, List

from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, UTCDateTimeType, IntType, DecimalType, \
    UUIDType, DateType, DictType, BaseType, UnionType

from .types import PassFortShareholding, PassFortMetadata, EntityData, \
    SearchInput, PassFortAssociate, OfficerRelationship, ShareholderRelationship, BeneficialOwnerRelationship, \
    Financials, Statement, StatementEntryBase, MonitoringEvent

from .fuzzy import CompanyNameMatcher
from .event_mappings import get_rule_code_to_monitoring_config

SUPPORTED_CURRENCIES = [c.alpha_3 for c in pycountry.currencies]
DIRECTOR_POSITIONS = [
    'Assistant Managing Director',
    'Chairman & Chief Executive',
    'Chairman & Director',
    'Chairman & Joint M.D.',
    'Chairman & Managing Director',
    'Chief Executive',
    'Commercial Director',
    'Corporate Nominee Director',
    'Deputy Chairman and MD',
    'Deputy Chief Executive',
    'Deputy Managing Director',
    'Director',
    'Director & Company Secretary',
    'Finance Director',
    'Financial Director',
    'Joint M.D. & Deputy Chairman',
    'Joint Managing Director',
    'Managing Director',
    'Managing Director & Dep.Chairman',
    'Marketing Director',
    'Non-Executive Director',
    'Personnel Director',
    'Producton Director',
    'Production Director',  # for when CreditSafe fixes their typo
    'Research Director',
    'Sales & Marketing Director',
    'Sales Director',
    'Technical Director',
    'Vice-Chairman & M.D.',
    'Works Director'
]

SECRETARY_POSITIONS = [
    'Company Secretary',
    'Corporate Nominee Secretary',
    'Director & Company Secretary',
    'Joint Secretary'
]

PARTNER_POSITIONS = [
    'Corporate LLP Designated Member',
    'Corporate LLP Member',
    'LLP Designated Member',
    'LLP Member'
]

'''
Known position names

Assistant Managing Director
Chairman,
Chairman & Chief Executive
Chairman & Director
Chairman & Joint M.D.
Chairman & Managing Director
Chartered Accountant
Chief Executive
CIC Manager
Commercial Director
Committee Member
Company Secretary
Corporate LLP Designated Member
Corporate LLP Member
Corporate Member Administritive
Corporate Member Management
Corporate Member Supervisory
Corporate Nominee Director
Corporate Nominee Secretary
Deputy Chairman
Deputy Chairman and MD
Deputy Chief Executive
Deputy Managing Director
Director
Director & Company Secretary
Finance Director
Financial Director
Head of Consultant Development
Joint Chairman
Joint Deputy Chairman
Joint M.D. & Deputy Chairman
Joint Managing Director
Joint Secretary
Judicial Factor
LLP Designated Member
LLP Member
Management Organisation Member
Manager (CAICE Act)
Managing Director
Managing Director & Dep.Chairman
Marketing Director
Member Admin, Organisation
Member of Administrative Organ
Member of Management
Member Supervisory Organisation
Non-Executive Director
Personnel Director
President
Producton Director
Receiver and Manager
Receiver/Manager (Charities Act)
Research Director
Sales & Marketing Director
Sales Director
Supervisory Organisation Member
Technical Director
The Company Solicitor
Trade Mark Manager
Vice Chairman
Vice President
Vice-Chairman & M.D.
Works Director
'''

INDIVIDUAL_ENTITY = 'INDIVIDUAL'
COMPANY_ENTITY = 'COMPANY'


def to_snake_case(input):
    return re.sub('(?!^)([A-Z]+)', r'_\1', input).lower()


def split_name(name, expect_title=False):
    parsed_name = nameparser.HumanName(name)
    given_names = parsed_name.first.split() + parsed_name.middle.split()
    family_name = parsed_name.last

    return given_names, family_name


def resolver_key(name, entity_type=INDIVIDUAL_ENTITY):
    lower_name = name.lower()
    if entity_type == INDIVIDUAL_ENTITY:
        given_names, family_name = split_name(lower_name)
        return ' '.join(given_names + [family_name]).strip()
    return lower_name.replace(',', '')


def build_resolver_id(original_id):
    return uuid.uuid3(uuid.NAMESPACE_X500, original_id)


class CreditsafeSingleShareholder(Model):
    entity_type = StringType(choices=[INDIVIDUAL_ENTITY, COMPANY_ENTITY], default=None)
    name = StringType(required=True)
    shareholdings = ListType(ModelType(PassFortShareholding), default=[], required=True)
    should_search = True

    @property
    def total_percentage(self):
        return float(sum(x.percentage for x in self.shareholdings if x.percentage is not None))

    def to_passfort_shareholder(self, entity_type, associate_id, search_data=None):
        if entity_type == INDIVIDUAL_ENTITY:
            first_names, last_name = split_name(self.name)
            immediate_data = EntityData.as_individual(first_names, last_name, search_data)
        else:
            immediate_data = EntityData.as_company(self.name, search_data)

        result = PassFortAssociate({
            'associate_id': associate_id,
            'entity_type': entity_type,
            'immediate_data': immediate_data,
            'relationships': []
        })
        result.relationships.append(ShareholderRelationship({
            'associated_role': 'SHAREHOLDER',
            'is_active': True,
            'shareholdings': [s.serialize() for s in self.shareholdings]
        }))
        return result


class OfficerPosition(Model):
    date_appointed = UTCDateTimeType(default=None, serialized_name="dateAppointed")
    position_name = StringType(default=None, serialized_name="positionName")


class CurrentOfficer(Model):
    _creditsafe_id = StringType(default=None, serialized_name="id")
    name = StringType(required=True)
    title = StringType(default=None)
    first_name = StringType(default=None, serialized_name="firstName")
    middle_name = StringType(default=None, serialized_name="middleName")
    surname = StringType(default=None)
    gender = StringType(default=None)
    dob = UTCDateTimeType(default=None, serialized_name="dateOfBirth")
    positions = ListType(ModelType(OfficerPosition), default=[])

    @property
    def id(self):
        if self._creditsafe_id is None:
            # Sometimes officers have no id?
            return resolver_key(self.name or 'None', self.entity_type)
        else:
            return self._creditsafe_id

    @property
    def entity_type(self):
        if self.name and (self.dob is not None or not (self.gender is None or self.gender == 'Unknown')):
            return INDIVIDUAL_ENTITY
        return None

    @property
    def default_entity_type(self):
        if self.entity_type:
            return self.entity_type
        if any(position.position_name in DIRECTOR_POSITIONS for position in self.positions):
            return INDIVIDUAL_ENTITY
        if any(position.position_name in SECRETARY_POSITIONS for position in self.positions):
            return COMPANY_ENTITY
        return INDIVIDUAL_ENTITY

    def format_name(self, entity_type):
        if entity_type == INDIVIDUAL_ENTITY:
            if self.first_name and self.surname:
                first_names = self.first_name.split(' ')
                if self.middle_name:
                    first_names.extend(self.middle_name.split(' '))
                return first_names, self.surname
            else:
                return split_name(self.name, expect_title=True)
        return None, self.name

    def to_immediate_data(self, entity_type, search_data=None):
        first_names, last_name = self.format_name(entity_type)
        if entity_type == INDIVIDUAL_ENTITY:
            return EntityData.as_individual(first_names, last_name, self.dob)
        else:
            return EntityData.as_company(last_name, search_data)

    def to_associate(self, entity_type, search_data):
        result = PassFortAssociate({
            'associate_id': build_resolver_id(self.id),
            'entity_type': entity_type,
            'immediate_data': self.to_immediate_data(entity_type, search_data),
            'relationships': []
        })

        for position in self.positions:
            roles = []

            if position.position_name in DIRECTOR_POSITIONS:
                roles.append('DIRECTOR')
            if position.position_name in SECRETARY_POSITIONS:
                roles.append('COMPANY_SECRETARY')
            if position.position_name in PARTNER_POSITIONS:
                roles.append('PARTNER')
            if len(roles) == 0:
                roles = ['OTHER']
            for role in roles:
                result.relationships.append(OfficerRelationship({
                    'original_role': position.position_name,
                    'appointed_on': position.date_appointed,
                    'associated_role': role,
                    'is_active': True
                }))
        if len(self.positions) == 0:
            result.relationships.append(OfficerRelationship({
                'original_role': 'Unknown',
                'associated_role': 'OTHER',
                'is_active': True
            }))
        return result


class PersonOfSignificantControl(Model):
    title = StringType(default=None)
    name = StringType(default=None)
    nationality = StringType(default=None)
    country = StringType(default=None)
    country_of_registration = StringType(default=None, serialized_name="countryOfRegistration")
    dob = UTCDateTimeType(default=None, serialized_name="dateOfBirth")
    registration_number = StringType(default=None, serialized_name="registrationNumber")
    legal_form = StringType(default=None, serialized_name="legalForm")
    kind = StringType(default=None)
    person_type = StringType(default=None, serialized_name="personType")

    @property
    def entity_type(self):
        if self.person_type == 'Person':
            return INDIVIDUAL_ENTITY
        if self.person_type == 'Company':
            return COMPANY_ENTITY
        if self.kind:
            if 'individual' in self.kind:
                return INDIVIDUAL_ENTITY
            else:
                return COMPANY_ENTITY
        # Duedil also returns None if it can't determine the entity type
        return None

    @property
    def country_of_nationality(self):
        from .nationality_to_ISO3 import convert_nationality_to_iso3
        if self.nationality:
            return convert_nationality_to_iso3(self.nationality)
        return None

    @property
    def country_of_incorporation(self):
        for country_name in [self.country_of_registration, self.country]:
            # Sometimes the country of registration is not searchable
            if country_name:
                country = pycountry.countries.get(
                    name=country_name) or pycountry.countries.get(official_name=country_name)
                if not country:
                    try:
                        country_list = pycountry.countries.search_fuzzy(country_name)
                        if len(country_list) == 1:
                            country = country_list[0]
                    except LookupError:
                        pass

                if country:
                    return country.alpha_3

        return None

    def to_associate(self, associate_id):
        if self.entity_type == INDIVIDUAL_ENTITY:
            first_names, last_name = split_name(self.name)
            immediate_data = EntityData.as_individual(
                first_names,
                last_name,
                self.dob,
                self.country_of_nationality,
                self.title
            )
        else:
            immediate_data = EntityData.as_company(self.name, search_data={
                'name': self.name,
                'number': self.registration_number,
                'country_of_incorporation': self.country_of_incorporation,
            })

        result = PassFortAssociate({
            'associate_id': associate_id,
            'entity_type': self.entity_type,
            'immediate_data': immediate_data,
            'relationships': []
        })

        result.relationships.append(BeneficialOwnerRelationship({
            'associated_role': 'BENEFICIAL_OWNER',
            'is_active': True,
        }))

        return result


class ProcessQueuePayload(Model):
    shareholder = ModelType(CreditsafeSingleShareholder, default=None)
    officer = ModelType(CurrentOfficer, default=None)
    psc = ModelType(PersonOfSignificantControl, default=None)
    entity_type = StringType(default=None)
    associate_id = UUIDType(required=True)
    result = ModelType(PassFortAssociate, default=None)

    def skip_search(self):
        # If this entity is a PSC, and we already have enough information,
        # don't do the extra search.
        if self.psc and \
                self.psc.country_of_incorporation and \
                self.psc.registration_number:
            return True
        # Or, if this entity is just a non PSC shareholder, don't do the extra
        # search on them if not required (>50 shareholders with larger holdings)
        if not self.officer and not self.psc:
            if self.shareholder and not self.shareholder.should_search:
                return True

        return False


class AssociateIdDeduplicator:
    associate_ids: Dict[str, uuid.UUID] = ...
    associate_ids_to_payload: Dict[uuid.UUID, 'ProcessQueuePayload'] = ...

    def __init__(self, directors_report: 'CompanyDirectorsReport'):
        # Converts to passfort format and in order to the shareholder names against the directors
        associate_ids = {}
        associate_ids_to_payload = {}
        if directors_report is not None:
            for d in directors_report.current_directors:
                key = resolver_key(d.name, d.entity_type or INDIVIDUAL_ENTITY)
                associate_ids[key] = build_resolver_id(d.id)
                associate_ids_to_payload[associate_ids[key]] = ProcessQueuePayload({
                    'officer': d,
                    'entity_type': d.entity_type,
                    'associate_id': associate_ids[key]
                })
        self.associate_ids = associate_ids
        self.associate_ids_to_payload = associate_ids_to_payload

    def find_or_create_associate_id(self, name, entity_type) -> uuid.UUID:
        name_key = resolver_key(name, entity_type)
        potential_associate_id = self.associate_ids.get(name_key)

        if potential_associate_id:
            return potential_associate_id

        return build_resolver_id(name_key)

    def add_shareholders(self, shareholders: List['CreditsafeSingleShareholder']):
        for unique_shareholder in shareholders:
            name_key = resolver_key(unique_shareholder.name, unique_shareholder.entity_type or 'COMPANY')
            associate_id = self.find_or_create_associate_id(
                unique_shareholder.name, unique_shareholder.entity_type or 'COMPANY')
            associate_payload = self.get_associate_payload_by_id(associate_id)

            if associate_payload:
                shareholder_type = unique_shareholder.entity_type
                if associate_payload.entity_type == INDIVIDUAL_ENTITY:
                    if shareholder_type is None or shareholder_type == associate_payload.entity_type:
                        associate_payload.shareholder = unique_shareholder
                    else:
                        # Super edge case when we find an officer that matches the name, but has a different entity type
                        # Make sure we assign a different uuid
                        associate_id = uuid.uuid4()
                        self.associate_ids[name_key] = associate_id
                        self.associate_ids_to_payload[associate_id] = ProcessQueuePayload({
                            'shareholder': unique_shareholder,
                            'entity_type': unique_shareholder.entity_type,
                            'associate_id': uuid.uuid4()
                        })
                else:
                    associate_payload.shareholder = unique_shareholder
                    associate_payload.entity_type = shareholder_type
            else:
                # No officer found to merge with
                self.associate_ids[name_key] = associate_id
                self.associate_ids_to_payload[associate_id] = ProcessQueuePayload({
                    'shareholder': unique_shareholder,
                    'entity_type': unique_shareholder.entity_type,
                    'associate_id': associate_id
                })

    def add_pscs(self, pscs: List['PersonOfSignificantControl']):
        for psc in pscs:
            name = psc.name
            associate_id = self.find_or_create_associate_id(name, psc.entity_type)
            associate_payload = self.get_associate_payload_by_id(associate_id)

            if associate_payload and (not associate_payload.entity_type or
                                      associate_payload.entity_type == psc.entity_type):

                associate_payload.entity_type = psc.entity_type
                associate_payload.psc = psc
            else:
                associate_id = uuid.uuid4()
                name_key = resolver_key(name, psc.entity_type)
                self.associate_ids[name_key] = associate_id
                self.associate_ids_to_payload[associate_id] = ProcessQueuePayload({
                    'psc': psc,
                    'entity_type': psc.entity_type,
                    'associate_id': associate_id
                })

    def get_associate_payload_by_id(self, associate_id: uuid.UUID) -> Optional['ProcessQueuePayload']:
        return self.associate_ids_to_payload.get(associate_id)

    def officers_payload(self, associate_ids: Set[uuid.UUID]) -> List['ProcessQueuePayload']:
        return [
            payload
            for res_id, payload in self.associate_ids_to_payload.items()
            if res_id not in associate_ids and payload.offcer
        ]

    def associates(self):
        return list(self.associate_ids_to_payload.values())


class CreditsafeSearchAddress(Model):
    province = StringType(default=None)


class CreditSafeCompanySearchResponse(Model):
    creditsafe_id = StringType(required=True, serialized_name="id")
    registration_number = StringType(default=None, serialized_name="regNo")
    name = StringType(default=None)
    address = ModelType(CreditsafeSearchAddress, default=None)

    def as_passfort_format(self, country, state):
        result = {
            'name': self.name,
            'number': self.registration_number,
            'creditsafe_id': self.creditsafe_id,
            'country_of_incorporation': country
        }
        state_from_search = self.address and self.address.province
        if state_from_search or state:
            result['state_of_incorporation'] = state_from_search or state
        return result

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def name_match_confidence(self, search):
        if not search.name:
            return 100
        if not self.name:
            return 0
        matcher = CompanyNameMatcher()
        return matcher.match_ratio(search.name, self.name)

    def matches_search(self, search: SearchInput, fuzz_factor) -> bool:
        numbers_present = search.number is not None and self.registration_number is not None
        matches_number = numbers_present and search.number.lower().strip() == self.registration_number.lower().strip()
        if numbers_present and not matches_number:
            return False

        # If Company number matches be less strict with name matching
        matcher = CompanyNameMatcher(50 if matches_number else fuzz_factor)
        names_present = search.name is not None and self.name is not None
        if names_present and not matcher.match(search.name, self.name):
            return False

        if search.state and self.address and self.address.province:
            if search.state != self.address.province:
                return False

        return True


class ContactAddress(Model):
    address_type = StringType(default=None, serialized_name="type")
    simple_value = StringType(default=None, serialized_name="simpleValue")
    postal_code = StringType(default=None, serialized_name="postalCode")
    country = StringType(default=None)

    @property
    def passfort_address_type(self):
        # TODO request a complete list of address types from CreditSafe
        supported_types = ['registered_address']  #, 'trading_address', 'contact_address']

        if self.address_type:
            address_enum = self.address_type.lower().replace(' ', '_')
            if address_enum in supported_types:
                return address_enum

        return None

    def as_passfort_address(self, default_country_code):
        country_code = self.country if self.country is not None else default_country_code

        if self.simple_value is None or country_code is None:
            return None

        return {
            'type': self.passfort_address_type,
            'address': {
                "type": 'FREEFORM',
                "text": self.simple_value,
                "country": pycountry.countries.get(alpha_2=country_code).alpha_3
            }
        }


class ContactInformation(Model):
    main_address = ModelType(ContactAddress, required=True, serialized_name="mainAddress")
    other_addresses = ListType(ModelType(ContactAddress), default=[], serialized_name="otherAddresses")


class CompanyLegalForm(Model):
    description = StringType(default='Unknown')


class CompanyBasicInformation(Model):
    name = StringType(required=True, serialized_name="registeredCompanyName")
    registration_date = UTCDateTimeType(default=None, serialized_name="companyRegistrationDate")
    legal_form = ModelType(CompanyLegalForm, serialized_name="legalForm", default=None)


class CompanyIdentification(Model):
    basic_info = ModelType(CompanyBasicInformation,
                           serialized_name="basicInformation",
                           required=True)

    @property
    def incorporation_date(self):
        return self.basic_info.registration_date

    @property
    def raw_company_type(self):
        return self.basic_info.legal_form.description if self.basic_info.legal_form else ''

    @property
    def structured_company_type(self):
        is_limited = None
        is_public = None
        ownership_type = None
        if self.raw_company_type:
            company_type_words = self.raw_company_type.lower().split(' ')
            if 'limited' in company_type_words:
                is_limited = True
            if 'unlimited' in company_type_words:
                is_limited = False
            if 'private' in company_type_words:
                is_public = False
            if 'public' in company_type_words:
                is_public = True
            if 'partnership' in company_type_words:
                ownership_type = 'PARTNERSHIP'

        return {
            'is_limited': is_limited,
            'is_public': is_public,
            'ownership_type': ownership_type
        }


class CompanyStatus(Model):
    status = StringType(default="Unknown")
    description = StringType(default=None)


class CompanyDirectorsReport(Model):
    current_directors = ListType(ModelType(CurrentOfficer), default=[], serialized_name="currentDirectors")


class Shareholder(Model):
    name = StringType(required=True)
    shareholder_type = StringType(default="Other", serialized_name="shareholderType")
    share_class = StringType(default=None, serialized_name="shareType")
    currency = StringType(default=None)
    amount = IntType(serialized_name="totalNumberOfSharesOwned", default=None)
    percentage = DecimalType(serialized_name="percentSharesHeld", default=None)

    def format_name(self, entity_type):
        if entity_type == INDIVIDUAL_ENTITY:
            return split_name(self.name, expect_title=False)
        return None, self.name

    @property
    def entity_type(self):
        if self.shareholder_type == 'Person':
            return INDIVIDUAL_ENTITY
        if self.shareholder_type == 'Company':
            return COMPANY_ENTITY
        return None

    @property
    def shareholding(self):
        return {
            'share_class': self.share_class,
            'currency': self.currency,
            'amount': self.amount,
            'percentage': self.percentage
        }


class ShareholdersReport(Model):
    shareholders = ListType(ModelType(Shareholder), default=[], serialized_name="shareHolders")

    def unique_shareholders(self):
        # Merge shareholdings for shareholders with the same name
        unique_shareholders = {}
        for s in self.shareholders:
            if s.name not in unique_shareholders:
                entity_type = s.entity_type

                unique_shareholders[s.name] = CreditsafeSingleShareholder({
                    'entity_type': entity_type,
                    'name': s.name,
                    'shareholdings': []
                })
            unique_shareholders[s.name].shareholdings.append(
                PassFortShareholding(s.shareholding)
            )
        return unique_shareholders.values()


class CompanySummary(Model):
    country = StringType(required=True)
    business_name = StringType(required=True, serialized_name="businessName")
    number = StringType(default=None, serialized_name="companyRegistrationNumber")
    status = ModelType(CompanyStatus, required=True, serialized_name="companyStatus")

    @property
    def country_code(self):
        return pycountry.countries.get(alpha_2=self.country).alpha_3

    @property
    def is_active(self):
        if self.status.status.lower() == 'active':
            return True
        if self.status.status.lower() == 'nonactive':
            return False
        return None


class PSCReport(Model):
    active_psc = ListType(ModelType(PersonOfSignificantControl), serialized_name="activePSC", default=[])


class CreditsafeMonetaryValue(Model):
    value = UnionType((DecimalType, StringType), default=None)
    currency = StringType(default=None)

    def to_json(self):
        if self.value is not None:
            try:
                return {
                    'value': float(self.value),
                    'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None
                }
            except ValueError:
                # No actual credit limit if we can't parse it
                return None
        return None


class ProviderCreditRating(Model):
    value = StringType(default=None)
    minValue = StringType(default=None)
    maxValue = StringType(default=None)


class SummarisedCreditRating(Model):
    international_value = StringType(serialized_name="commonValue", default=None)
    international_description = StringType(serialized_name="commonDescription", default=None)
    credit_limit = ModelType(CreditsafeMonetaryValue, serialized_name="creditLimit", default=None)
    provider_value = ModelType(ProviderCreditRating, serialized_name="providerValue", default=None)
    provider_description = StringType(serialized_name="providerDescription", default=None)

    def to_json(self):
        result = {}

        if self.international_value:
            result['international_rating'] = {
                'value': self.international_value,
                'description': self.international_description
            }
        if self.provider_value:
            result['credit_rating'] = {
                'value': self.provider_value.value,
                'description': self.provider_description
            }
        if self.credit_limit:
            credit_limit = self.credit_limit.to_json()
            result['credit_limit'] = credit_limit

        return result


class CreditScore(Model):
    current_contract_limit = ModelType(CreditsafeMonetaryValue, serialized_name="currentContractLimit", default=None)
    current_credit_rating = ModelType(SummarisedCreditRating, serialized_name="currentCreditRating", default=None)
    previous_credit_rating = ModelType(SummarisedCreditRating, serialized_name="previousCreditRating", default=None)
    latest_rating_date = UTCDateTimeType(serialized_name="latestRatingChangeDate", default=None)


class CompanyRating(Model):
    date = UTCDateTimeType(required=True)
    value = IntType(default=None, serialized_name="companyValue")
    description = StringType(default=None, serialized_name="ratingDescription")

    def to_json(self):
        if self.value is not None:
            return {
                'value': str(self.value),
                'description': self.description
            }
        return None


class CreditLimit(Model):
    date = UTCDateTimeType(required=True)
    monetary_value = ModelType(CreditsafeMonetaryValue, default=None, serialized_name="companyValue")

    def to_json(self):
        return self.monetary_value and self.monetary_value.to_json()


class AdditionalInformation(Model):
    psc_report = ModelType(PSCReport, serialized_name="personsWithSignificantControl", default=None)
    credit_limit_history = ListType(ModelType(CreditLimit), serialized_name="creditLimitHistory", default=[])
    rating_history = ListType(ModelType(CompanyRating), serialized_name="ratingHistory", default=[])


class CreditsafeFinancialStatement(Model):
    currency = StringType(default=None)
    _is_consolidated = BooleanType(serialized_name="consolidatedAccounts", default=None)
    _scope = StringType(serialized_name="type", required=True)
    date = UTCDateTimeType(serialized_name="yearEndDate", required=True)
    profit_and_loss = DictType(BaseType, default={}, serialized_name="profitAndLoss")
    balance_sheet = DictType(BaseType, default={}, serialized_name="balanceSheet")
    other_financials = DictType(BaseType, default={}, serialized_name="otherFinancials")

    @property
    def is_consolidated(self):
        return False if self._is_consolidated is None else self._is_consolidated

    def parse_dict_entries(self, group_map, input_dict):
        entries = []
        groups = []
        for k, v in group_map.items():
            groups.append({
                'name': to_snake_case(k),
                'value': {
                    'value': input_dict.get(k, None),
                    'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                },
                'value_type': 'CURRENCY'
            })
            for item in v:
                entries.append({
                    'name': to_snake_case(item),
                    'value_type': 'CURRENCY',
                    'value': {
                        'value': input_dict.get(item, None),
                        'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                    },
                    'group_name': to_snake_case(k)
                })
        return entries, groups


class CreditsafeGlobalFinancialStatement(CreditsafeFinancialStatement):

    @property
    def scope(self):
        # Deal with creditsafe inconsistent data...
        if self._scope == 'GGS Standardised':
            return 'GlobalFinancialsGGS'
        return self._scope

    def to_json(self):
        pl_map = {
            'revenue': [],
            'operatingProfit': [
                'operatingCosts',
            ],
            'profitBeforeTax': [
                'pensionCosts',
                'wagesAndSalaries',
                'financialIncome',
                'financialExpenses',
                'extraordinaryIncome',
                'extraordinaryCosts',
                'depreciation',
                'amortisation'
            ],
            'profitAfterTax': [
                'tax'
            ],
            'retainedProfit': [
                'dividends',
                'minorityInterests',
                'otherAppropriations'
            ]
        }

        balance_map = {
            'cash': [],
            'totalReceivables': [
                'tradeReceivables',
                'groupReceivables',
                'receivablesDueAfter1Year',
                'miscellaneousReceivables'
            ],
            'totalInventories': [
                'rawMaterials',
                'workInProgress',
                'finishedGoods',
                'otherInventories'
            ],
            'totalCurrentAssets': [
                'otherCurrentAssets'
            ],
            'totalTangibleAssets': [
                'landAndBuildings',
                'plantAndMachinery',
                'otherTangibleAssets'
            ],
            'totalOtherFixedAssets': [
                'investments',
                'loansToGroup',
                'otherLoans',
                'miscellaneousFixedAssets'
            ],
            'totalIntangibleAssets': [
                'goodwill',
                'otherIntangibleAssets'
            ],
            'totalFixedAssets': [],
            'totalCurrentLiabilities': [
                'tradePayables',
                'bankLiabilities',
                'otherLoansOrFinance',
                'groupPayables',
                'miscellaneousLiabilities'
            ],
            'totalLongTermLiabilities': [
                'tradePayablesDueAfter1Year',
                'bankLiabilitiesDueAfter1Year',
                'otherLoansOrFinanceDueAfter1Year',
                'groupPayablesDueAfter1Year',
                'miscellaneousLiabilitiesDueAfter1Year'
            ]
        }

        cap_and_reserves_map = {
            'totalShareholdersEquity': [
                'calledUpShareCapital',
                'sharePremium',
                'revenueReserves',
                'otherReserves'
            ]
        }

        other_financials_map = {
            'netWorth': [],	 # otherFinancials
            'workingCapital': [],  # otherFinancials
            'totalAssets': [],  # balanceSheet
            'totalLiabilities': [],  # balanceSheet
        }

        pl_entries, pl_groups = self.parse_dict_entries(pl_map, self.profit_and_loss)
        balance_entries, balance_groups = self.parse_dict_entries(
            balance_map, self.balance_sheet)

        cap_and_reserves_entries, cap_and_reserves_groups = self.parse_dict_entries(
            cap_and_reserves_map, self.balance_sheet)

        other_fin_entries, other_fin_groups = self.parse_dict_entries(
            other_financials_map, {**self.balance_sheet, **self.other_financials})

        return [
            {
                'statement_type': 'PROFIT_AND_LOSS',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': pl_entries,
                'groups': pl_groups
            },
            {
                'statement_type': 'BALANCE_SHEET',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': balance_entries,
                'groups': balance_groups
            },
            {
                'statement_type': 'CAPITAL_AND_RESERVES',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': cap_and_reserves_entries,
                'groups': cap_and_reserves_groups
            },
            {
                'statement_type': 'OTHER_FINANCIAL_ITEMS',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': other_fin_entries,
                'groups': other_fin_groups
            }
        ]


class CreditsafeLocalFinancialStatement(CreditsafeFinancialStatement):
    cash_flow = DictType(BaseType, default={}, serialized_name="cashFlow")

    @property
    def scope(self):
        return self._scope

    def to_json(self):
        pl_map = {
            'turnover': [],
            'operatingProfit': [
                'exports',
                'costOfSales',
                'grossProfit',
                'wagesAndSalaries',
                'directorsRemuneration'
            ],
            'profitBeforeTax': ['depreciation', 'auditFees', 'interestExpense'],
            'retainedProfit': ['taxation', 'profitAfterTax', 'dividends']
        }

        balance_map = {
            'totalFixedAssets': ['tangibleAssets', 'intangibleAssets'],
            'totalCurrentAssets': ['cash', 'stock', 'tradeDebtors', 'otherDebtors', 'miscCurrentAssets'],
            'totalCurrentLiabilities': [
                'tradeCreditors', 'bankBorrowingsCurrent', 'otherShortTermFinance', 'miscCurrentLiabilities'
            ],
            'totalLongTermLiabilities': ['bankOverdraftAndLTL', 'otherLongTermFinance']
        }

        cap_and_reserves_map = {
            'totalShareholdersEquity': [
                'issuedShareCapital', 'revaluationReserve', 'revenueReserves', 'otherReserves'
            ]
        }

        # Use groups with no other entries for single items
        # (keeps the logic simple in the UI, no need to worry about loose entries)
        other_financials_map = {
            'netWorth': [],	 # otherFinancials
            'workingCapital': [],  # otherFinancials
            'totalAssets': [],  # balanceSheet
            'totalLiabilities': [],  # balanceSheet
            'netAssets': [],  # balanceSheet
        }

        cash_flow_map = {
            'netCashFlowFromOperations': [],
            'netCashFlowBeforeFinancing': [],
            'netCashFlowFromFinancing': [],
            'increaseInCash': [],
        }

        pl_entries, pl_groups = self.parse_dict_entries(pl_map, self.profit_and_loss)
        balance_entries, balance_groups = self.parse_dict_entries(
            balance_map, {**self.other_financials, **self.balance_sheet})

        cap_and_reserves_entries, cap_and_reserves_groups = self.parse_dict_entries(
            cap_and_reserves_map, self.balance_sheet)

        other_fin_entries, other_fin_groups = self.parse_dict_entries(
            other_financials_map, {**self.balance_sheet, **self.other_financials})

        cash_flow_entries, cash_flow_groups = self.parse_dict_entries(
            cash_flow_map, self.cash_flow)

        return [
            {
                'statement_type': 'PROFIT_AND_LOSS',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': pl_entries,
                'groups': pl_groups
            },
            {
                'statement_type': 'BALANCE_SHEET',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': balance_entries,
                'groups': balance_groups
            },
            {
                'statement_type': 'CAPITAL_AND_RESERVES',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': cap_and_reserves_entries,
                'groups': cap_and_reserves_groups
            },
            {
                'statement_type': 'OTHER_FINANCIAL_ITEMS',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': other_fin_entries,
                'groups': other_fin_groups
            },
            {
                'statement_type': 'CASH_FLOW',
                'statement_format': self.scope,
                'date': self.date,
                'currency_code': self.currency if self.currency in SUPPORTED_CURRENCIES else None,
                'entries': cash_flow_entries,
                'groups': cash_flow_groups
            }
        ]


class CreditSafeCompanyReport(Model):
    creditsafe_id = StringType(required=True, serialized_name="companyId")
    summary = ModelType(CompanySummary, required=True, serialized_name="companySummary")
    identification = ModelType(CompanyIdentification, required=True, serialized_name="companyIdentification")
    contact_information = ModelType(ContactInformation, default=None, serialized_name="contactInformation")
    directors = ModelType(CompanyDirectorsReport, default=None)
    share_capital_structure = ModelType(ShareholdersReport, default=None, serialized_name="shareCapitalStructure")
    additional_information = ModelType(AdditionalInformation, default=None, serialized_name="additionalInformation")
    credit_score = ModelType(CreditScore, serialized_name="creditScore", default=None)
    local_financial_statements = ListType(ModelType(CreditsafeLocalFinancialStatement),
                                          serialized_name="localFinancialStatements", default=[])
    global_financial_statements = ListType(ModelType(CreditsafeGlobalFinancialStatement),
                                           serialized_name="financialStatements", default=[])

    @property
    def credit_limit_history(self):
        if self.additional_information:
            return self.additional_information.credit_limit_history
        return []

    @property
    def rating_history(self):
        if self.additional_information:
            return self.additional_information.rating_history
        return []

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    @classmethod
    def get_filtered_statements(cls, raw_statements, scope, is_consolidated):
        return sorted(
            list(chain(
                *[s.to_json() for s in raw_statements
                  if s.scope == scope and s.is_consolidated == is_consolidated])),
            key=lambda x: x['date'],
            reverse=True
        )

    @property
    def statements(self):
        '''
        Returns local and global statements. in order to keep the numbers consistent,
        only returns consolidated or non consolidated accounts, defaulting to non consolidated.
        '''
        local_non_consolidated_statements = self.get_filtered_statements(
            self.local_financial_statements, 'LocalFinancialsCSUK', is_consolidated=False)

        global_non_consolidated_statements = self.get_filtered_statements(
            self.global_financial_statements, 'GlobalFinancialsGGS', is_consolidated=False)

        statements = local_non_consolidated_statements + global_non_consolidated_statements

        if len(statements) == 0:
            # Try to get the consolidated ones then

            local_consolidated_statements = self.get_filtered_statements(
                self.local_financial_statements, 'LocalFinancialsCSUK', is_consolidated=True)

            global_consolidated_statements = self.get_filtered_statements(
                self.global_financial_statements, 'GlobalFinancialsGGS', is_consolidated=True)
            statements = local_consolidated_statements + global_consolidated_statements

        return statements

    def to_financials(self):
        contract_limit = None
        current_international_rating = None
        previous_international_rating = None

        if self.credit_score:
            if self.credit_score.current_contract_limit:
                contract_limit = self.credit_score.current_contract_limit.to_json()
            if self.credit_score.current_credit_rating:
                current_international_rating = self.credit_score.current_credit_rating.to_json()
            if self.credit_score.previous_credit_rating:
                previous_international_rating = self.credit_score.previous_credit_rating.to_json()

        credit_history_dict = defaultdict(lambda: defaultdict(dict))
        for rating, limit in zip_longest(self.rating_history, self.credit_limit_history, fillvalue=None):
            if rating:
                credit_history_dict[rating.date]['credit_rating'] = rating.to_json()
            if limit:
                credit_history_dict[limit.date]['credit_limit'] = limit.to_json()

        credit_history = sorted(
            [{'date': k, **v} for k, v in credit_history_dict.items()],
            key=lambda elem: elem['date'],
            reverse=True
        )

        if credit_history:
            # Just make sure we add them in order.
            if current_international_rating:
                credit_history[0].update(current_international_rating)
            if previous_international_rating and len(credit_history) > 1:
                credit_history[1].update(previous_international_rating)
        elif current_international_rating:
            credit_history = [
                {
                    'date': self.credit_score.latest_rating_date,
                    **current_international_rating
                }
            ]

        financials = Financials({
            'contract_limit': contract_limit,
            'credit_history': credit_history,
            'statements': self.statements
        })
        financials.validate()

        for s_type in [
            'PROFIT_AND_LOSS', 'BALANCE_SHEET', 'CAPITAL_AND_RESERVES', 'OTHER_FINANCIAL_ITEMS', 'CASH_FLOW'
        ]:
            with_yoy([s for s in financials.statements if s.statement_type == s_type])
        return financials

    def as_passfort_format_41(self, request_handler=None):
        addresses = [
            self.contact_information.main_address.as_passfort_address(self.summary.country)
        ] if self.contact_information else []

        if self.contact_information:
            addresses.extend([
                address.as_passfort_address(self.summary.country)
                for address in self.contact_information.other_addresses
                if address.passfort_address_type is not None
            ])

        metadata = PassFortMetadata({
            'name': self.identification.basic_info.name,
            'number': self.summary.number,
            'addresses': addresses,
            'country_of_incorporation': self.summary.country_code,
            'is_active': self.summary.is_active,
            'incorporation_date': self.identification.incorporation_date,
            'company_type': self.identification.raw_company_type,
            'structured_company_type': self.identification.structured_company_type,
        })

        unique_shareholders = sorted(
            self.share_capital_structure.unique_shareholders(),
            key=lambda s: s.total_percentage, reverse=True
        ) if self.share_capital_structure else []

        # Only perform an additional search on the first 50 non-PSC shareholders
        for sh in unique_shareholders[50:]:
            sh.should_search = False

        pscs = []
        if self.additional_information and self.additional_information.psc_report:
            pscs = [
                psc
                for psc in self.additional_information.psc_report.active_psc
                if psc.entity_type and psc.name
            ]

        associates = merge_associates(
            self.directors,
            unique_shareholders,
            pscs,
            self.summary.country_code,
            request_handler)

        return {
            'metadata': metadata.serialize(),
            'financials': self.to_financials().serialize(),
            'associated_entities': [a.serialize() for a in associates]
        }


def process_associate_data(associate_data: 'ProcessQueuePayload', country, request_handler=None):
    search_data = None
    default_entity = associate_data.entity_type
    if associate_data.entity_type != INDIVIDUAL_ENTITY:
        default_entity = INDIVIDUAL_ENTITY
        if associate_data.psc:
            name = associate_data.psc.name
            if associate_data.psc.entity_type is not None:
                default_entity = associate_data.psc.entity_type
        elif associate_data.shareholder:
            name = associate_data.shareholder.name
            if associate_data.shareholder.entity_type is not None:
                default_entity = associate_data.shareholder.entity_type
        else:
            # Officer has lowest priority as CreditSafe does not communicate whether
            # an officer is an individual or person reliably
            name = associate_data.officer.name
            default_entity = associate_data.officer.default_entity_type

        if request_handler and not associate_data.skip_search():
            # only search if we have to
            search_data = request_handler.exact_search(name, country)

    entity_type = COMPANY_ENTITY if search_data else default_entity
    result = None
    if associate_data.shareholder:
        result = associate_data.shareholder.to_passfort_shareholder(
            entity_type,
            associate_data.associate_id,
            search_data
        )

    if associate_data.officer:
        officer_associate = associate_data.officer.to_associate(entity_type, search_data)

        if result:
            result.merge(officer_associate)
        else:
            result = officer_associate

    if associate_data.psc is not None:
        psc_associate = associate_data.psc.to_associate(associate_data.associate_id)
        if result:
            result.merge(psc_associate)
        else:
            result = psc_associate

    associate_data.result = result
    return result


def merge_associates(
        directors,
        unique_shareholders,
        pscs,
        country_of_incorporation,
        request_handler):
    duplicate_resolver = AssociateIdDeduplicator(directors)
    duplicate_resolver.add_shareholders(unique_shareholders)
    duplicate_resolver.add_pscs(pscs)

    processing_queue = duplicate_resolver.associates()

    with concurrent.futures.ThreadPoolExecutor(max_workers=10) as executor:
        jobs = [executor.submit(process_associate_data, obj, country_of_incorporation, request_handler)
                for obj in processing_queue]
        concurrent.futures.wait(jobs, return_when=concurrent.futures.FIRST_EXCEPTION)
        failed_jobs = filter(lambda e: e is not None, map(lambda j: j.exception(), jobs))
        try:
            e = next(failed_jobs)
        except StopIteration:
            pass
        else:
            raise e

    return [a.result for a in processing_queue]


def calculate_yoy(crt_year_entries: List[StatementEntryBase], prev_year_entries: List[StatementEntryBase]):
    for entry in crt_year_entries:
        crt_value = entry.value and entry.value.value
        if entry.value_type == 'CURRENCY' and crt_value is not None:
            prev_entry_value = next((e.value and e.value.value for e in prev_year_entries if e.name == entry.name),
                                    None)
            entry.yoy = None
            if prev_entry_value is not None and prev_entry_value != 0:
                entry.yoy = (crt_value - prev_entry_value) / abs(prev_entry_value)


def with_yoy(sorted_statements: List[Statement]):
    # Should only be used with statements of the same type
    if len(sorted_statements) < 2:
        return

    for i in range(len(sorted_statements) - 1):
        crt = sorted_statements[i]
        prev_year = sorted_statements[i + 1]

        calculate_yoy(crt.entries, prev_year.entries)
        calculate_yoy(crt.groups, prev_year.groups)


class CreditSafePortfolio(Model):
    id = IntType(required=True, serialized_name="portfolioId")
    name = StringType(required=True)
    is_default = BooleanType(serialized_name="isDefault")
    correlation_id = UUIDType(serialized_name="correlationId")

    @classmethod
    def from_json(cls, data: dict) -> 'CreditSafePortfolio':
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model


class CreditSafeNotificationPaging(Model):
    size = IntType(required=True)

    # These could be null if there is only one page
    prev = IntType()
    next = IntType()

    last = IntType(required=True)


class CreditSafeCompanyData(Model):
    id = StringType(required=True)
    safe_number = StringType(serialized_name='safeNumber')
    name = StringType()
    country_code = StringType(serialized_name='countryCode')
    portfolio_id = IntType(required=True, serialized_name='portfolioId')
    portfolio_name = StringType(serialized_name='portfolioName')


class CreditSafeNotificationEvent(Model):
    company = ModelType(CreditSafeCompanyData, required=True)
    event_id = IntType(serialized_name='eventId')
    event_date = StringType(serialized_name='eventDate')

    # This was found in their API response but not documented in the Creditsafe API docs...
    created_date = StringType(serialized_name='createdDate')

    new_value = StringType(serialized_name='newValue')
    old_value = StringType(serialized_name='oldValue')
    notification_event_id = IntType(serialized_name='notificationEventId')
    rule_code = IntType(serialized_name='ruleCode', required=True)
    rule_name = StringType(serialized_name='ruleName')

    def to_passfort_format(self):
        rule_code_to_monitoring_config = get_rule_code_to_monitoring_config()

        event_type = rule_code_to_monitoring_config.get(self.rule_code)
        if event_type is not None:
            event = MonitoringEvent({
                'creditsafe_id': self.company.id,
                'event_type': event_type.value,
                'event_date': self.event_date,
                'rule_code': self.rule_code
            })

            event.validate()
            return event

        return None


class EventsConfigGroup:
    last_run_date: datetime
    portfolio_id: int
    raw_events: List[CreditSafeNotificationEvent]

    def __init__(self, last_run_date, portfolio_id, raw_events):
        super().__init__()

        self.last_run_date = last_run_date
        self.portfolio_id = portfolio_id
        self.raw_events = raw_events


class CreditSafeNotificationEventsResponse(Model):
    total_count = IntType(serialized_name='totalCount')
    data = ListType(ModelType(CreditSafeNotificationEvent), default=[])
    paging = ModelType(CreditSafeNotificationPaging)

    @classmethod
    def from_json(cls, data: dict) -> 'CreditSafeNotificationEventsResponse':
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model
