from typing import Optional, List
from flask import abort, request, jsonify
from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import StringType, BooleanType, ModelType, FloatType
from schematics.exceptions import DataError, ValidationError
from functools import wraps

from .error import Error

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
                errors = e.to_primitive()
                if errors.get('credentials') is not None:
                    response = jsonify(Error.provider_misconfiguration_error('Credentials is required'))
                    if(isinstance(errors['credentials'], dict)):
                       response = jsonify(Error.provider_misconfiguration_error('Apikey is required'))
                else:
                    response = jsonify(Error.bad_api_request(e))
                response.status_code = 400
                abort(response)

            return fn(model, *args, **kwargs)

        return wrapped_fn

    return validates_model


class PassFortAddress(Model):
    type = StringType(choices=['STRUCTURED', 'FREEFORM'], required=True)
    country = StringType(required=True)
    state = StringType(default=None)
    premise = StringType(default=None)
    locality = StringType(default=None)
    postal_code = StringType(default=None)
    county = StringType(default=None)
    latitude = FloatType(default=None)
    longitude = FloatType(default=None)

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_loqate(cls, loqate_address: 'LoqateAddress'):
        state = getattr(loqate_address, 'administrative_area', None) \
            if loqate_address.country in ['USA', 'CAN'] \
            else None
        data = {
            "type": "STRUCTURED",
            "country": loqate_address.country,
            "state": state,
            "premise": getattr(loqate_address, 'premise', None),
            "postal_code": getattr(loqate_address, 'postal_code', None),
            "locality": getattr(loqate_address, 'locality', None),
            "county": getattr(loqate_address, 'sub_administrative_area'),
            "latitude": getattr(loqate_address, 'latitude', None),
            "longitude": getattr(loqate_address, 'longitude', None),
        }

        return cls().import_data(data, apply_defaults=True)


class LoqateAddress(Model):
    country = StringType(required=True, serialized_name="Country")
    premise = StringType(default=None, serialized_name="Premise")
    locality = StringType(default=None, serialized_name="Locality")
    postal_code = StringType(default=None, serialized_name="PostalCode")
    administrative_area = StringType(default=None, serialized_name="AdministrativeArea")
    sub_administrative_area = StringType(default=None, serialized_name="SubAdministrativeArea")
    latitude = FloatType(default=None, serialized_name="Latitude")
    longitude = FloatType(default=None, serialized_name="Longitude")

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, passfort_address: 'PassFortAddress'):
        data = {
            "Country": passfort_address.country,
            "Premise": getattr(passfort_address, 'premise', None),
            "Locality": getattr(passfort_address, 'locality', None),
            "PostalCode": getattr(passfort_address, 'postal_code', None),
            "AdministrativeArea": getattr(passfort_address, 'state', None),
            "SubAdministrativeArea": getattr(passfort_address, 'county', None),
        }
        return cls().import_data(data, apply_defaults=True)

    @classmethod
    def from_raw(cls, raw_data: dict):
        clean_data = {k:v for k,v in raw_data.items() if v is not ""}

        address = cls().import_data(clean_data)
        address.validate()
        return address

class Config(Model):
    use_certified_dataset = BooleanType(default=False)

class Credentials(Model):
    apikey: str = StringType(required=True)

class CheckInput(Model):
    address: PassFortAddress = ModelType(PassFortAddress, required=True)

class GeoCodingCheck(Model):
    config: Config = ModelType(Config)
    credentials: Credentials = ModelType(Credentials, required=True)
    input_data: CheckInput = ModelType(CheckInput, required=True)
    is_demo: bool = BooleanType(default=False)

    def to_request_body(self):
        return {
            'Key': self.config.apikey,
            # This should become a config option in the future
            # if the check will be used for other purposes
            # as this option incurs extra chargers
            'Geocode': True,
            'Addresses': [self.input_data.address.to_primitive()],
            'Certify': self.config.use_certified_dataset,
        }

