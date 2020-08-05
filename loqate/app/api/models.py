from typing import Optional, List
from flask import abort, request, jsonify
from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import StringType, BooleanType, ModelType, FloatType, ListType
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
    route = StringType(default=None)
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
        premise = getattr(loqate_address, 'premise', None) or getattr(loqate_address, 'building', None)
        data = {
            "type": "STRUCTURED",
            "country": loqate_address.country_iso3,
            "state": state,
            "premise": premise,
            "route": getattr(loqate_address, 'thoroughfare', None),
            "postal_code": getattr(loqate_address, 'postal_code', None),
            "locality": getattr(loqate_address, 'locality', None),
            "county": getattr(loqate_address, 'sub_administrative_area', None),
            "latitude": getattr(loqate_address, 'latitude', None),
            "longitude": getattr(loqate_address, 'longitude', None),
        }

        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model


class LoqateAddress(Model):
    country_iso3 = StringType(serialized_name="ISO3166-3")
    country = StringType(required=True, serialized_name="Country")
    premise = StringType(default=None, serialized_name="Premise")
    locality = StringType(default=None, serialized_name="Locality")
    building = StringType(default=None, serialized_name='Building')
    postal_code = StringType(default=None, serialized_name="PostalCode")
    administrative_area = StringType(default=None, serialized_name="AdministrativeArea")
    sub_administrative_area = StringType(default=None, serialized_name="SubAdministrativeArea")
    thoroughfare = StringType(default=None, serialized_name="Thoroughfare")
    latitude = FloatType(default=None, serialized_name="Latitude")
    longitude = FloatType(default=None, serialized_name="Longitude")

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort(cls, passfort_address: PassFortAddress) -> 'LoqateAddress':
        data = {
            "ISO3166-3": passfort_address.country,
            "Country": passfort_address.country,
            "Premise": getattr(passfort_address, 'premise', None),
            "Locality": getattr(passfort_address, 'locality', None),
            "PostalCode": getattr(passfort_address, 'postal_code', None),
            "AdministrativeArea": getattr(passfort_address, 'state', None),
            "SubAdministrativeArea": getattr(passfort_address, 'county', None),
            "Thoroughfare": getattr(passfort_address, 'route', None),
        }
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    @classmethod
    def from_raw(cls, raw_data: dict) -> 'LoqateAddress':
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
    config: Config = ModelType(Config, default={})
    credentials: Credentials = ModelType(Credentials, required=True)
    input_data: CheckInput = ModelType(CheckInput, required=True)
    is_demo: bool = BooleanType(default=False)

    def to_request_body(self):
        return {
            'Key': self.credentials.apikey,
            # This should become a config option in the future
            # if the check will be used for other purposes
            # as this option incurs extra chargers
            'Geocode': True,
            'Addresses': [LoqateAddress.from_passfort(self.input_data.address).to_primitive()],
            'Certify': self.config.use_certified_dataset,
        }

geo_accuracy_statuses = {
    'P': 'POINT',
    'I': 'INTERPOLATED',
    'A': 'AVERAGE',
    'U': 'FAILED',
}

geo_accuracy_levels = {
    '5': 'DELIVERY_POINT',
    '4': 'PREMISE',
    '3': 'THOROUGHFARE',
    '2': 'LOCALITY',
    '1': 'ADMINISTRATIVE_AREA',
}

class GeoCodingMatch(LoqateAddress):
    geo_accuracy: str = StringType(serialized_name="GeoAccuracy")

    def get_geo_accuracy(self):
        if getattr(self, 'geo_accuracy', None) and len(self.geo_accuracy) == 2:
            status, level = self.geo_accuracy
            return {
                'status': geo_accuracy_statuses.get(status),
                'level': geo_accuracy_levels.get(level)
            }
        else:
            return {
                'status': 'FAILED'
            }

class GeoCodingResponse(Model):
    input_address: LoqateAddress = ModelType(LoqateAddress, required=True)
    matches: List[GeoCodingMatch] = ListType(ModelType(GeoCodingMatch))

    @property
    def geocoding_match(self) -> GeoCodingMatch:
        # Just pick the first match for now
        return self.matches[0] if self.matches else None

    @classmethod
    def from_raw(cls, data: list) -> 'GeoCodingResponse':
        # pick the first one as we only send one address
        data = data[0] if data else {}
        model = cls().import_data({
            'input_address': data.get('Input'),
            'matches': data.get('Matches'),
        })
        model.validate()
        return model
