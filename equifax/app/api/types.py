import datetime
from enum import unique, Enum
from flask import abort, request
from functools import wraps

from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types import ModelType, BooleanType, StringType, ListType, DateType


def validate_model(validation_model):
    """
    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

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


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    MISCONFIGURATION_ERROR = 205

    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303

    UNKNOWN_INTERNAL_ERROR = 401


@unique
class MatchField(Enum):
    FORENAME = "FORENAME"
    SURNAME = "SURNAME"
    ADDRESS = "ADDRESS"
    DOB = "DOB"


@unique
class DatabaseType(Enum):
    CIVIL = "CIVIL"
    CREDIT = "CREDIT"
    MORTALITY = "MORTALITY"


class Error:

    @staticmethod
    def provider_connection_error(e):
        return {
            'code': ErrorCode.PROVIDER_CONNECTION_ERROR.value,
            'source': 'PROVIDER',
            'message': 'Connection error when contacting Equifax',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def provider_unknown_error(e):
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': 'There was an error calling Equifax',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def from_exception(e):
        return {
            'code': ErrorCode.UNKNOWN_INTERNAL_ERROR.value,
            'source': 'ENGINE',
            'message': '{}'.format(e)
        }

    @staticmethod
    def bad_api_request(e):
        return {
            'code': ErrorCode.INVALID_INPUT_DATA.value,
            'source': 'API',
            'message': 'Bad API request',
            'info': e.to_primitive()
        }


def validate_partial_date(value):
    for fmt in ['%Y-%m-%d', '%Y-%m', '%Y']:
        try:
            return datetime.datetime.strptime(value, fmt)
        except (ValueError, TypeError):
            continue
    raise ValidationError(f'Input is not valid date: {value}')


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    # Store dob as string. dateType loses the information on whether it's a partial date or not
    dob = StringType(required=True)

    def validate_dob(self, data, value):
        if value:
            validate_partial_date(value)
        return value


class StructuredAddress(Model):
    postal_code = StringType(required=True)
    state_province = StringType(required=True)
    postal_town = StringType(default=None)
    locality = StringType(default=None)
    street_number = StringType(default=None)
    route = StringType(default=None)

    def as_equifax_address(self):
        from collections import OrderedDict
        return OrderedDict([
            ('@addressType', 'CURR'),
            ('CivicNumber', self.street_number),
            ('StreetName', self.route),
            ('City', self.locality or self.postal_town),
            ('Province', OrderedDict([('@code', self.state_province)])),
            ('PostalCode', self.postal_code)
        ])


class AddressHistory(Model):
    current = ModelType(StructuredAddress, required=True)


class IndividualData(Model):
    personal_details = ModelType(PersonalDetails, required=True)
    address_history = ModelType(AddressHistory, required=True)

    @property
    def first_name(self):
        return self.personal_details.name.given_names[0] if len(self.personal_details.name.given_names) else ''

    @property
    def last_name(self):
        return self.personal_details.name.family_name

    @property
    def dob(self):
        return self.personal_details.dob


class EquifaxCredentials(Model):
    customer_code = StringType(required=True)
    customer_number = StringType(required=True)
    security_code = StringType(required=True)

    use_test_environment = BooleanType(required=True, default=False)

    @property
    def root_url(self):
        if self.use_test_environment:
            return 'https://uat.equifax.ca'
        else:
            return 'https://www.equifax.ca'


class EKYCRequest(Model):
    input_data = ModelType(IndividualData, required=True)
    credentials = ModelType(EquifaxCredentials, required=True)

    is_demo = BooleanType(default=False)
