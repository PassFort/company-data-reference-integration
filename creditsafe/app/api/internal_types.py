import pycountry
import uuid
import nameparser
import concurrent.futures

from collections import defaultdict
from typing import Dict, Optional, Set, List

from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, UTCDateTimeType, IntType, DecimalType, \
    UUIDType, DateType

from .types import PassFortOfficer, PassFortShareholder, PassFortShareholding, PassFortMetadata, EntityData, \
    SearchInput, PassFortAssociatev41, OfficerRelationship, ShareholderRelationship, BeneficialOwnerRelationship

from .fuzzy import CompanyNameMatcher

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
    'Production Director', # for when CreditSafe fixes their typo
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


def split_name(name, expect_title=False):
    parsed_name = nameparser.HumanName(name)
    given_names = parsed_name.first.split() + parsed_name.middle.split()
    family_name = parsed_name.last

    return given_names, family_name


def resolver_key(name, entity_type=INDIVIDUAL_ENTITY):
    lower_name = name.lower()
    if entity_type == INDIVIDUAL_ENTITY:
        given_names, family_name = split_name(lower_name)
        return ' '.join(given_names + [family_name])
    return lower_name.replace(',', '')


def build_resolver_id(original_id):
    return uuid.uuid3(uuid.NAMESPACE_X500, original_id)


class CreditsafeSingleShareholder(Model):
    entity_type = StringType(choices=[INDIVIDUAL_ENTITY, COMPANY_ENTITY], default=None)
    name = StringType(required=True)
    shareholdings = ListType(ModelType(PassFortShareholding), required=True)

    @property
    def total_percentage(self):
        return float(sum(x.percentage for x in self.shareholdings))

    def to_passfort_shareholder(self, entity_type, associate_id, search_data=None):
        if entity_type == INDIVIDUAL_ENTITY:
            first_names, last_name = split_name(self.name)
            immediate_data = EntityData.as_individual(first_names, last_name, search_data)
        else:
            immediate_data = EntityData.as_company(self.name, search_data)

        result = PassFortAssociatev41({
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
    def original_role(self):
        return self.positions.position_name

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
        result = PassFortAssociatev41({
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
        return result

    def to_passfort_officer_roles(self, request_handler, country_of_incorporation):
        search_data = None

        entity_type = self.entity_type
        if entity_type != INDIVIDUAL_ENTITY and request_handler:
            search_data = request_handler.exact_search(self.name, country_of_incorporation)

            if search_data:
                entity_type = COMPANY_ENTITY
            else:
                entity_type = INDIVIDUAL_ENTITY

        expanded_result = []
        if not entity_type and any(position.position_name in SECRETARY_POSITIONS for position in self.positions):
            entity_type = COMPANY_ENTITY
        else:
            entity_type = INDIVIDUAL_ENTITY

        for position in self.positions:
            expanded_result.append(PassFortOfficer({
                'resolver_id': build_resolver_id(self.id),
                'entity_type': entity_type,
                'immediate_data': self.to_immediate_data(entity_type, search_data),
                'original_role': position.position_name,
                'appointed_on': position.date_appointed
            }))
        return expanded_result


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
                country = pycountry.countries.get(name=country_name) or pycountry.countries.get(official_name=country_name)
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

    def to_passfort_shareholder(self):
        if self.name and self.entity_type:
            if self.entity_type == INDIVIDUAL_ENTITY:
                first_names, last_name = split_name(self.name, expect_title=True)
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
            return PassFortShareholder({
                'resolver_id': uuid.uuid4(),
                'immediate_data': immediate_data,
                'entity_type': self.entity_type,
            })
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

        result = PassFortAssociatev41({
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
    result = ModelType(PassFortAssociatev41, default=None)


class ResolverIdMatcher:
    resolver_ids: Dict[str, uuid.UUID] = ...
    resolver_ids_to_officers: Dict[uuid.UUID, 'CurrentOfficer'] = ...

    def __init__(self, directors_report: 'CompanyDirectorsReport'):
        # Converts to passfort format and in order to the shareholder names against the directors
        resolver_ids = {}
        resolver_ids_to_officers = {}
        if directors_report is not None:
            for d in directors_report.current_directors:
                key = resolver_key(d.name, d.entity_type or INDIVIDUAL_ENTITY)
                resolver_ids[key] = build_resolver_id(d.id)
                resolver_ids_to_officers[resolver_ids[key]] = d
        self.resolver_ids = resolver_ids
        self.resolver_ids_to_officers = resolver_ids_to_officers

    def find_or_create_resolver_id(self, shareholder_name, entity_type) -> uuid.UUID:
        name_key = resolver_key(shareholder_name, entity_type)
        potential_resolver_id = self.resolver_ids.get(name_key)

        if potential_resolver_id:
            return potential_resolver_id

        return build_resolver_id(name_key)

    def get_director_by_resolver_id(self, resolver_id: uuid.UUID) -> Optional['CurrentOfficer']:
        return self.resolver_ids_to_officers.get(resolver_id)


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
        non_matched = []
        for unique_shareholder in shareholders:
            name_key = resolver_key(unique_shareholder.name, unique_shareholder.entity_type)
            associate_id = self.find_or_create_associate_id(
                unique_shareholder.name, unique_shareholder.entity_type)
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
        return self.associate_ids_to_payload.values()


class CreditsafeSearchAddress(Model):
    province = StringType(default=None)


class CreditSafeCompanySearchResponse(Model):
    creditsafe_id = StringType(required=True, serialized_name="id")
    registration_number = StringType(default=None, serialized_name="regNo")
    name = StringType(required=True)
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
        matcher = CompanyNameMatcher()
        return matcher.match_ratio(search.name, self.name)

    def matches_search(self, search: SearchInput, fuzz_factor) -> bool:
        numbers_present = search.number is not None and self.registration_number is not None
        matches_number = numbers_present and search.number.lower().strip() == self.registration_number.lower().strip()
        if numbers_present and not matches_number:
            return False

        # If Company number matches be less strict with name matching
        matcher = CompanyNameMatcher(50 if matches_number else fuzz_factor)

        if search.name and not matcher.match(search.name, self.name):
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
        supported_types = ['registered_address', 'trading_address', 'contact_address']

        if self.address_type:
            address_enum = self.address_type.lower().replace(' ', '_')
            if address_enum in supported_types:
                return address_enum

        return None

    def as_passfort_address(self):
        if self.simple_value is None or self.country is None:
            return None
        return {
            'type': self.passfort_address_type,
            'address': {
                "type": 'FREEFORM',
                "text": self.simple_value,
                "country": pycountry.countries.get(alpha_2=self.country).alpha_3
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

    def officers(self):
        return [d.officer_base_data() for d in self.current_directors]

    def to_serialized_passfort_format(self, request_handler, country_of_incorporation):
        directors = []
        secretaries = []
        partners = []
        other = []
        for officer in self.current_directors:
            formatted_officer_by_role = officer.to_passfort_officer_roles(
                request_handler,
                country_of_incorporation
            )

            for officer_by_role in formatted_officer_by_role:
                is_other = True

                if officer_by_role['original_role'] in DIRECTOR_POSITIONS:
                    directors.append(officer_by_role)
                    is_other = False
                if officer_by_role['original_role'] in SECRETARY_POSITIONS:
                    secretaries.append(officer_by_role)
                    is_other = False
                if officer_by_role['original_role'] in PARTNER_POSITIONS:
                    partners.append(officer_by_role)
                    is_other = False
                if is_other:
                    other.append(officer_by_role)

        return {
            'directors': [d.serialize() for d in directors],
            'secretaries': [s.serialize() for s in secretaries],
            'partners': [p.serialize() for p in partners],
            'other': [o.serialize() for o in other]
        }


class Shareholder(Model):
    name = StringType(required=True)
    shareholder_type = StringType(default="Other", serialized_name="shareholderType")
    share_class = StringType(default=None, serialized_name="shareType")
    currency = StringType(default=None)
    amount = IntType(serialized_name="totalNumberOfSharesOwned", default=None)
    percentage = DecimalType(serialized_name="percentSharesHeld", required=True)

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

    def merge_shareholdings(self, request_handler, country_of_incorporation) -> Dict[str, 'PassFortShareholder']:
        # Merge shareholdings for shareholders with the same name
        unique_shareholders = {}
        for s in self.shareholders:
            if s.name not in unique_shareholders:
                search_data = None
                entity_type = s.entity_type
                if entity_type != 'INDIVIDUAL' and request_handler:
                    search_data = request_handler.exact_search(s.name, country_of_incorporation)
                    if search_data:
                        entity_type = 'COMPANY'

                first_names, last_name = s.format_name(entity_type)
                unique_shareholders[s.name] = PassFortShareholder({
                    'entity_type': entity_type,
                    'immediate_data':
                        EntityData.as_company(
                            last_name, search_data
                        ) if entity_type == 'COMPANY' else EntityData.as_individual(
                            first_names, last_name, search_data),
                    'shareholdings': []
                })

            unique_shareholders[s.name].shareholdings.append(
                PassFortShareholding(s.shareholding)
            )
        return unique_shareholders

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

    def as_passfort_format(self, resolver_id_matcher, request_handler, country_of_incorporation):
        unique_shareholders = self.merge_shareholdings(request_handler, country_of_incorporation)
        for name, passfort_shareholder in unique_shareholders.items():
            passfort_shareholder.resolver_id = resolver_id_matcher.find_or_create_resolver_id(
                name, passfort_shareholder.entity_type)

            director_data: 'CurrentOfficer' = resolver_id_matcher.get_director_by_resolver_id(
                passfort_shareholder.resolver_id
            )
            if director_data:
                if passfort_shareholder.entity_type == INDIVIDUAL_ENTITY:
                    dst_data = passfort_shareholder.immediate_data
                    src_data = director_data.to_immediate_data(INDIVIDUAL_ENTITY)
                    # Dob is the only field that needs merging for now (we match on name and search the other fields)
                    if src_data.personal_details.dob and not dst_data.personal_details.dob:
                        dst_data.personal_details.dob = src_data.personal_details.dob

        return [ds.serialize() for ds in unique_shareholders.values()]


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


class AdditionalInformation(Model):
    psc_report = ModelType(PSCReport, serialized_name="personsWithSignificantControl", default=None)


class CreditSafeCompanyReport(Model):
    creditsafe_id = StringType(required=True, serialized_name="companyId")
    summary = ModelType(CompanySummary, required=True, serialized_name="companySummary")
    identification = ModelType(CompanyIdentification, required=True, serialized_name="companyIdentification")
    contact_information = ModelType(ContactInformation, required=True, serialized_name="contactInformation")
    directors = ModelType(CompanyDirectorsReport, default=None)
    share_capital_structure = ModelType(ShareholdersReport, default=None, serialized_name="shareCapitalStructure")
    additional_information = ModelType(AdditionalInformation, default=None, serialized_name="additionalInformation")

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def as_passfort_format(self, request_handler = None):
        addresses = [
            self.contact_information.main_address.as_passfort_address()
        ]
        addresses.extend([
            address.as_passfort_address()
            for address in self.contact_information.other_addresses
        ])

        metadata = PassFortMetadata({
            'name': self.identification.basic_info.name,
            'number': self.summary.number,
            'addresses': addresses,
            'country_of_incorporation': self.summary.country_code,
            'is_active': self.summary.is_active,
            'incorporation_date': self.identification.incorporation_date,
            'company_type': self.identification.raw_company_type,
            'structured_company_type': self.identification.structured_company_type
        })

        officers = self.directors.to_serialized_passfort_format(
            request_handler,
            self.summary.country_code
        ) if self.directors else []

        shareholders = self.share_capital_structure.as_passfort_format(
            ResolverIdMatcher(self.directors),
            request_handler,
            self.summary.country_code
        ) if self.share_capital_structure else []

        pscs = []

        if self.additional_information and self.additional_information.psc_report:
            pscs = [psc.to_passfort_shareholder() for psc in self.additional_information.psc_report.active_psc]
        return {
            'metadata': metadata.serialize(),
            'officers': officers,
            'ownership_structure': {
                'shareholders': shareholders
            }
        }

    def as_passfort_format_41(self, request_handler = None):
        addresses = [
            self.contact_information.main_address.as_passfort_address()
        ]
        addresses.extend([
            address.as_passfort_address()
            for address in self.contact_information.other_addresses
        ])

        metadata = PassFortMetadata({
            'name': self.identification.basic_info.name,
            'number': self.summary.number,
            'addresses': addresses,
            'country_of_incorporation': self.summary.country_code,
            'is_active': self.summary.is_active,
            'incorporation_date': self.identification.incorporation_date,
            'company_type': self.identification.raw_company_type,
            'structured_company_type': self.identification.structured_company_type
        })
        unique_shareholders = sorted(
            self.share_capital_structure.unique_shareholders(),
            key=lambda s: s.total_percentage, reverse=True
        ) if self.share_capital_structure else []

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
            'associated_entities': [a.serialize() for a in associates]
        }


def process_associate_data(associate_data: 'ProcessQueuePayload', country, request_handler=None):
    search_data = None
    default_entity = associate_data.entity_type
    if associate_data.entity_type != INDIVIDUAL_ENTITY:
        default_entity = COMPANY_ENTITY
        if associate_data.officer:
            default_entity = INDIVIDUAL_ENTITY
            name = associate_data.officer.name
        elif associate_data.shareholder:
            name = associate_data.shareholder.name
        else:
            name = associate_data.psc.name

        if request_handler:
            if not associate_data.psc or not \
                    associate_data.psc.country_of_incorporation or not associate_data.psc.registration_number:
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
        for obj in processing_queue:
            executor.submit(process_associate_data, obj, country_of_incorporation, request_handler)

    return [a.result for a in processing_queue]