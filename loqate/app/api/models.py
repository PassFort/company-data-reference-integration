from typing import Optional, List
from flask import abort, request, jsonify
from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import StringType, BooleanType, ModelType, FloatType, ListType
from schematics.exceptions import DataError, ValidationError
from functools import wraps
from datetime import date

from .error import Error

COUNTRY_MAPPING = {
    # Loqate still thinks that Kosovo is part of Serbia...
    'UNK': 'SRB'
}


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
                    response = jsonify(Error.provider_misconfiguration_error(
                        'Credentials is required'))
                    if(isinstance(errors['credentials'], dict)):
                        response = jsonify(
                            Error.provider_misconfiguration_error('Apikey is required'))
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
    street_number = StringType(default=None)
    county = StringType(default=None)
    latitude = FloatType(default=None)
    longitude = FloatType(default=None)
    original_freeform_address = StringType(default=None)

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_loqate(cls, loqate_address: 'LoqateAddress') -> Optional['PassFortAddress']:
        premise = getattr(loqate_address, 'premise', None) or getattr(
            loqate_address, 'building', None)
        data = {
            "type": "STRUCTURED",
            "country": getattr(loqate_address, 'country_iso3', None),
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
    country_iso3 = StringType(default=None, serialized_name="ISO3166-3")
    country = StringType(default=None, serialized_name="Country")
    premise = StringType(default=None, serialized_name="Premise")
    locality = StringType(default=None, serialized_name="Locality")
    building = StringType(default=None, serialized_name="Building")
    postal_code = StringType(default=None, serialized_name="PostalCode")
    administrative_area = StringType(
        default=None, serialized_name="AdministrativeArea")
    sub_administrative_area = StringType(
        default=None, serialized_name="SubAdministrativeArea")
    thoroughfare = StringType(default=None, serialized_name="Thoroughfare")
    latitude = FloatType(default=None, serialized_name="Latitude")
    longitude = FloatType(default=None, serialized_name="Longitude")
    address1 = StringType(default=None, serialized_name="Address1")
    address2 = StringType(default=None, serialized_name="Address2")
    address3 = StringType(default=None, serialized_name="Address3")
    address4 = StringType(default=None, serialized_name="Address4")
    address5 = StringType(default=None, serialized_name="Address5")
    address6 = StringType(default=None, serialized_name="Address6")
    address7 = StringType(default=None, serialized_name="Address7")
    address8 = StringType(default=None, serialized_name="Address8")

    class Options:
        export_level = NOT_NONE

    @classmethod
    def from_passfort_structured(cls, passfort_address: PassFortAddress, use_address1=False) -> 'LoqateAddress':
        thoroughfare = ' '.join(
            filter(None, [
                getattr(passfort_address, 'street_number', None),
                getattr(passfort_address, 'route', None)
            ])
        )

        mapped_country = COUNTRY_MAPPING.get(
            passfort_address.country, passfort_address.country)

        thoroughfare_key = "Address1" if use_address1 else "Thoroughfare"

        data = {
            "ISO3166-3": mapped_country,
            "Country": mapped_country,
            "Premise": getattr(passfort_address, 'premise', None),
            "Locality": getattr(passfort_address, 'locality', None),
            "PostalCode": getattr(passfort_address, 'postal_code', None),
            "AdministrativeArea": getattr(passfort_address, 'state_province', None),
            "SubAdministrativeArea": getattr(passfort_address, 'county', None),
            thoroughfare_key: thoroughfare or None,
        }
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    @classmethod
    def from_passfort_freeform(cls, passfort_address: PassFortAddress) -> 'LoqateAddress':
        mapped_country = COUNTRY_MAPPING.get(
            passfort_address.country, passfort_address.country)

        data = {
            "ISO3166-3": mapped_country,
            "Country": mapped_country,
            "PostalCode": getattr(passfort_address, 'postal_code', None),
            "AdministrativeArea": getattr(passfort_address, 'state_province', None),
        }

        address_lines = passfort_address.original_freeform_address.split(',')
        index = 1
        for address_line in address_lines:
            stripped_line = address_line.strip()
            if not stripped_line:
                continue

            data[f"Address{index}"] = stripped_line
            index += 1
            if index > 8:
                break

        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model

    @classmethod
    def from_passfort(cls, passfort_address: PassFortAddress) -> 'LoqateAddress':
        if date.today().day % 2 == 0:
            return cls.from_passfort_structured(passfort_address, use_address1=True)
        else:
            return cls.from_passfort_structured(passfort_address)

    @classmethod
    def from_raw(cls, raw_data: dict) -> 'LoqateAddress':
        clean_data = {k: v for k, v in raw_data.items() if v != ""}

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
            'Options': {
                'ServerOptions': {
                    'MinimumGeoaccuracyLevel': 1,
                    'MaximumGeodistance': -1,
                }
            }
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
