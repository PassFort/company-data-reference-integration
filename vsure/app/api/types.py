import datetime
from enum import unique, Enum
from flask import request, abort
from functools import wraps
from schematics import Model
from schematics.exceptions import DataError
from schematics.types import BooleanType, StringType, ModelType, DateType, ListType


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
    PROVIDER_CONNECTION_ERROR = 302


class Error(object):

    @staticmethod
    def bad_api_request(e):
        return {
            'code': ErrorCode.INVALID_INPUT_DATA.value,
            'source': 'API',
            'message': 'Bad API request',
            'info': e.to_primitive()
        }

    @staticmethod
    def provider_connection_error(e):
        return {
            'code': ErrorCode.PROVIDER_CONNECTION_ERROR.value,
            'source': 'PROVIDER',
            'message': 'Connection error when contacting vSure',
            'info': {
                'raw': '{}'.format(e)
            }
        }


class VSureConfig(Model):
    visa_check_type = StringType(choices=['WORK', 'STUDY'], required=True)


class VSureCredentials(Model):
    api_key = StringType(required=True)

    @property
    def base_url(self):
        return "https://api.vsure.com.au/v1/"


def validate_partial_date(value):
    try:
        return datetime.datetime.strptime(value, '%Y-%m-%d')
    except (ValueError, TypeError):
        raise ValidationError(f'Input is not valid date: {value}')


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    dob = StringType(required=True)

    def validate_dob(self, data, value):
        if value:
            validate_partial_date(value)
        return value


class StructuredAddress(Model):
    country = StringType(required=True)


class DocumentMetadata(Model):
    document_type = StringType(choices=["PASSPORT"], required=True)
    number = StringType(required=True)
    country_code = StringType(required=True)


class IndividualData(Model):
    personal_details = ModelType(PersonalDetails, required=True)
    documents_metadata = ListType(ModelType(DocumentMetadata), required=True, min_size=1)

    @property
    def given_names(self):
        return ' '.join(self.personal_details.name.given_names)

    @property
    def family_name(self):
        return self.personal_details.name.family_name

    @property
    def date_of_birth(self):
        return self.personal_details.dob

    @property
    def passport_id(self):
        return self.documents_metadata[0].number

    @property
    def country(self):
        return self.documents_metadata[0].country_code


class VisaCheckRequest(Model):
    config = ModelType(VSureConfig, required=True)
    credentials = ModelType(VSureCredentials, required=True)

    input_data = ModelType(IndividualData, required=True)

    is_demo = BooleanType(default=False)
