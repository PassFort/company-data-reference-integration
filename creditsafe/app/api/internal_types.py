import pycountry
import uuid

from collections import defaultdict

from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, UTCDateTimeType, IntType, DecimalType, \
    UUIDType, DateType

from .types import PassFortOfficer, PassFortShareholder, PassFortShareholding, PassFortMetadata


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


def split_name(name, expect_title=False):
    names = name.split(' ')
    start = 0
    # First name is the title.
    if expect_title:
        start = 1
    # Assume the last is the surname.
    # It can be in any order, and it won't depend necessarily on the country, but on the quality of data.
    return names[start:-1], names[-1]


def resolver_key(name, expect_title=False):
    lower_name = name.lower()
    if expect_title:
        parts = lower_name.split(' ', maxsplit=1)
        if len(parts) == 1:
            return parts[0]
        return parts[1]
    else:
        return lower_name


def build_resolver_id(original_id):
    return uuid.uuid3(uuid.NAMESPACE_X500, original_id)


class CreditSafeCompanySearchResponse(Model):
    creditsafe_id = StringType(required=True, serialized_name="id")
    registration_number = StringType(default=None, serialized_name="regNo")
    name = StringType(required=True)

    def as_passfort_format(self, country, state):
        result = {
            'name': self.name,
            'number': self.registration_number,
            'creditsafe_id': self.creditsafe_id,
            'country_of_incorporation': country
        }
        if state:
            result['state_of_incorporation'] = state
        return result


    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model


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
        if self.simple_value is None:
            return None
        return {
            'type': self.passfort_address_type,
            'address': {
                "type": 'FREEFORM',
                "text": self.simple_value,
                "country": pycountry.countries.get(alpha_2=self.country).alpha_3 if self.country else None
            }
        }


class ContactInformation(Model):
    main_address = ModelType(ContactAddress, required=True, serialized_name="mainAddress")
    other_addresses = ListType(ModelType(ContactAddress), default=[], serialized_name="otherAddresses")


class CompanyLegalForm(Model):
    description = StringType(required=True)


class CompanyBasicInformation(Model):
    name = StringType(required=True, serialized_name="registeredCompanyName")
    registration_date = UTCDateTimeType(default=None, serialized_name="companyRegistrationDate")
    legal_form = ModelType(CompanyLegalForm, serialized_name="legalForm", required=True)


class CompanyIdentification(Model):
    basic_info = ModelType(CompanyBasicInformation,
                           serialized_name="basicInformation",
                           required=True)

    @property
    def incorporation_date(self):
        return self.basic_info.registration_date

    @property
    def raw_company_type(self):
        return self.basic_info.legal_form.description

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


class OfficerPosition(Model):
    date_appointed = UTCDateTimeType(default=None, serialized_name="dateAppointed")
    position_name = StringType(default=None, serialized_name="positionName")


class CurrentOfficer(Model):
    id = StringType(required=True)
    name = StringType(default=None)
    title = StringType(default=None)
    first_name = StringType(default=None, serialized_name="firstName")
    middle_name = StringType(default=None, serialized_name="middleName")
    surname = StringType(default=None)
    dob = UTCDateTimeType(default=None, serialized_name="dateOfBirth")
    positions = ListType(ModelType(OfficerPosition), default=[])

    @property
    def entity_type(self):
        if self.name and not (self.title or self.first_name or self.middle_name):
            return 'COMPANY'
        return 'INDIVIDUAL'

    @property
    def original_role(self):
        return self.positions.position_name

    def format_name(self):
        if self.entity_type == 'INDIVIDUAL':
            if self.first_name and self.surname:
                first_names = self.first_name.split(' ')
                if self.middle_name:
                    first_names.extend(self.middle_name.split(' '))
                return first_names, self.surname
            else:
                return split_name(self.name, expect_title=True)
        return None, self.name

    def to_passfort_officer_roles(self):
        first_names, last_name = self.format_name()
        expanded_result = []

        for position in self.positions:
            expanded_result.append(PassFortOfficer({
                'resolver_id': build_resolver_id(self.id),
                'type': self.entity_type,
                'first_names': first_names,
                'last_name': last_name,
                'original_role': position.position_name,
                'appointed_on': position.date_appointed,
                'dob': self.dob
            }))
        return expanded_result


class CompanyDirectorsReport(Model):
    current_directors = ListType(ModelType(CurrentOfficer), default=[], serialized_name="currentDirectors")

    def to_serialized_passfort_format(self):
        directors = []
        secretaries = []
        partners = []
        other = []
        for officer in self.current_directors:
            formatted_officer_by_role = officer.to_passfort_officer_roles()

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
    shareholder_type = StringType(required=True, choices=["Person", "Company"], serialized_name="shareholderType")
    share_class = StringType(default=None, serialized_name="shareType")
    currency = StringType(default=None)
    amount = IntType(serialized_name="totalNumberOfSharesOwned", required=True)
    percentage = DecimalType(serialized_name="percentSharesHeld", required=True)

    def format_name(self):
        if self.entity_type == 'INDIVIDUAL':
            return split_name(self.name, expect_title=False)
        return None, self.name

    @property
    def entity_type(self):
        if self.shareholder_type == 'Person':
            return 'INDIVIDUAL'
        if self.shareholder_type == 'Company':
            return 'COMPANY'
        raise NotImplementedError()

    @property
    def shareholding(self):
        return {
            'share_class': self.share_class,
            'currency': self.currency,
            'amount': self.amount,
            'percentage': self.percentage
        }


class ShareholdersReport(Model):
    shareholders = ListType(ModelType(Shareholder), default=None, serialized_name="shareHolders")

    def as_passfort_format(self, resolver_ids_by_name):
        deduplicated_shareholders = {}
        for s in self.shareholders:
            if deduplicated_shareholders.get(s.name) is None:
                name_key = resolver_key(s.name, expect_title=False)
                potential_resolver_id = resolver_ids_by_name.get(name_key)
                resolver_id = potential_resolver_id if potential_resolver_id is not None \
                    else build_resolver_id(name_key)

                first_names, last_name = s.format_name()
                deduplicated_shareholders[s.name] = PassFortShareholder({
                    'resolver_id': resolver_id,
                    'type': s.entity_type,
                    'last_name': last_name,
                    'shareholdings': [s.shareholding]
                })
                if s.entity_type == 'INDIVIDUAL':
                    deduplicated_shareholders[s.name].first_names = first_names
            else:
                deduplicated_shareholders[s.name].shareholdings.append(
                    PassFortShareholding(s.shareholding)
                )

        for _, ds in deduplicated_shareholders.items():
            ds.total_percentage = sum(x.percentage for x in ds.shareholdings)

        return [ds.serialize() for ds in deduplicated_shareholders.values()]


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


class CreditSafeCompanyReport(Model):
    creditsafe_id = StringType(required=True, serialized_name="companyId")
    summary = ModelType(CompanySummary, required=True, serialized_name="companySummary")
    identification = ModelType(CompanyIdentification, required=True, serialized_name="companyIdentification")
    contact_information = ModelType(ContactInformation, required=True, serialized_name="contactInformation")
    directors = ModelType(CompanyDirectorsReport, default=None)
    share_capital_structure = ModelType(ShareholdersReport, default=None, serialized_name="shareCapitalStructure")

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    def as_passfort_format(self):
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

        officers = self.directors.to_serialized_passfort_format() if self.directors else []
        resolver_ids = self.flatten_resolver_ids()
        shareholders = self.share_capital_structure.as_passfort_format(
            resolver_ids) if self.share_capital_structure else []
        return {
            'metadata': metadata.serialize(),
            'officers': officers,
            'ownership_structure': {
                'shareholders': shareholders
            }
        }

    def flatten_resolver_ids(self):
        # Converts to passfort format and resolves the shareholder names against the directors
        resolver_id_by_name = {}
        if self.directors is None:
            return {}

        for d in self.directors.current_directors:
            key = resolver_key(d.name, expect_title=True)
            resolver_id_by_name[key] = build_resolver_id(d.id)
        return resolver_id_by_name
