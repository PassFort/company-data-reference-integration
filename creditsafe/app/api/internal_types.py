import pycountry

from datetime import datetime

from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, UTCDateTimeType


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
    simple_value = StringType(required=True, serialized_name="simpleValue")
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
        return {}


class CompanyStatus(Model):
    status = StringType(default="Unknown")
    description = StringType(default=None)


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

        metadata = {
            'name': self.identification.basic_info.name,
            'number': self.summary.number,
            'addresses': addresses,
            'country_of_incorporation': self.summary.country_code,
            'is_active': self.summary.is_active,
            'incorporation_date': self.identification.incorporation_date,
            'company_type': self.identification.raw_company_type,
            'structured_company_type': self.identification.structured_company_type
        }
        return metadata
