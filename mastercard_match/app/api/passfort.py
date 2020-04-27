from schematics.exceptions import ValidationError, DataError
from schematics.models import Model
from schematics.types import StringType, ListType, ModelType, DictType
from flask import request, abort
from functools import wraps
from typing import List, Optional
from .errors import Error


def validate_model(validation_model):
    '''
    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    '''

    def validates_model(fn):
        @wraps(fn)
        def wrapped_fn(*args, **kwargs):
            model = None
            try:
                model = validation_model().import_data(request.json, apply_defaults=True)
                model.validate()
            except DataError as e:
                abort(400, Error.bad_api_request(e))

            return fn(model, *args, **kwargs)

        return wrapped_fn

    return validates_model


class Address(Model):
    postal_code = StringType(default=None)
    postal_town = StringType(default=None)
    locality = StringType(default=None)
    state_province = StringType(default=None)
    route = StringType(default=None)
    street_number = StringType(default=None)
    premise = StringType(default=None)
    subpremise = StringType(default=None)
    country = StringType(required=True)
    address_lines = StringType(default=None)

    def validate_state_province(self, data, value):
        if data.get('country') in ['CAN', 'USA'] and not value:
            raise ValidationError('State is required for Canada and United States addresses')
        return value

    def validate_locality(self, data, value):
        if not data.get('postal_town') and not value:
            raise ValidationError('Postal town or locality is requied')
        return value

    def validate_route(self, data, value):
        props = ['route', 'street_number', 'premise', 'subpremise']
        if not any(data.get(p) for p in props):
            raise ValidationError(f'Need at least one of {props} to build line1 of address')
        return value


class AddressWrapper(Model):
    address: Address = ModelType(Address, required=True)


class FullName(Model):
    family_name = StringType(required=True)
    given_names = ListType(StringType, required=True)

    @property
    def middle_initial(self):
        if len(self.given_names) > 1:
            return self.given_names[1][0].upper()
        return None


class PersonalDetails(Model):
    name: FullName = ModelType(FullName, required=True)
    address_history: List[AddressWrapper] = ListType(ModelType(AddressWrapper), required=True, min_size=1)
    national_identity_number = DictType(StringType(), default={})

    @property
    def current_address(self) -> Address:
        return self.address_history[0].address

    @property
    def national_id(self):
        return next((v for k, v in self.national_identity_number.items()), None)


class ContactDetails(Model):
    phone_number = StringType(default=None)


class DocumentMetadata(Model):
    document_type = StringType(required=True)
    number = StringType(required=True)
    country_code = StringType(required=True)
    issuing_state = StringType(default=None)


class IndividualData(Model):
    personal_details: PersonalDetails = ModelType(PersonalDetails)
    contact_details: ContactDetails = ModelType(ContactDetails, default={})
    document_metadata: DocumentMetadata = ListType(ModelType(DocumentMetadata), default=[])

    @property
    def drivers_license(self) -> DocumentMetadata:
        return next((doc for doc in self.document_metadata if doc.document_type == 'DRIVING_LICENCE'), None)


class CompanyContactDetails(Model):
    phone_number = StringType(default=None)
    url = StringType(default=None)


class CompanyMetadata(Model):
    name = StringType(required=True)
    addresses = ListType(ModelType(AddressWrapper), required=True, min_size=1)
    contact_details: CompanyContactDetails = ModelType(CompanyContactDetails, default={})

    @property
    def first_address(self) -> Address:
        return self.addresses[0].address


class CompanyData(Model):
    metadata: CompanyMetadata = ModelType(CompanyMetadata, required=True)
    associated_entities: List[IndividualData] = ListType(ModelType(IndividualData), required=True, min_size=1)

    def import_data(self, raw_data, **kwargs):
        if raw_data:
            entities = raw_data.get('associated_entities')
            if entities:
                raw_data['associated_entities'] = [e for e in entities if e.get('entity_type') == 'INDIVIDUAL']
        return super(CompanyData, self).import_data(raw_data, **kwargs)


class MatchConfig(Model):
    acquirer_id = StringType(required=True)


class MatchCredentials(Model):
    certificate = StringType(required=True)
    consumer_key = StringType(required=True)


class InquiryRequest(Model):
    config: MatchConfig = ModelType(MatchConfig, required=True)
    credentials: MatchCredentials = ModelType(MatchCredentials, required=True)
    input_data: CompanyData = ModelType(CompanyData, required=True)
