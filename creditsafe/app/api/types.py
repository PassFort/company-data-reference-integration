import pycountry

from enum import unique, Enum
from flask import abort, g, request
from functools import wraps

from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types import BooleanType, StringType, ModelType

# TODO JSONDECODE
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


class CreditSafeError(Exception):

    def __init__(self, response):
        self.response = response


class CreditSafeAuthenticationError(CreditSafeError):
    pass


class CreditSafeSearchError(CreditSafeError):
    pass


class CreditSafeReportError(CreditSafeError):
    pass


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    MISCONFIGURATION_ERROR = 205

    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303

    UNKNOWN_INTERNAL_ERROR = 401


class Error:

    @staticmethod
    def bad_api_request(e):
        return {
            'code': ErrorCode.INVALID_INPUT_DATA.value,
            'source': 'API',
            'message': 'Bad API request',
            'info': e.to_primitive()
        }

    @staticmethod
    def provider_unhandled_error(provider_message: str):
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': 'Provider unhandled error',
            'info': {
                'provider_error': {
                    'message': provider_message
                }
            }
        }


class CreditSafeCredentials(Model):
    username = StringType(required=True)
    password = StringType(required=True)


class SearchInput(Model):
    # Name or company number
    query = StringType(required=True)
    country = StringType(required=True, choices=[c.alpha_3 for c in pycountry.countries])
    state = StringType(default=None)

    def get_creditsafe_country(self):
        country = pycountry.countries.get(alpha_3=self.country)
        return country.alpha_2

    def build_queries(self):
        country_code = self.get_creditsafe_country()

        name_query = f'name={self.query}'
        registered_number_query = f'regNo={self.query}'
        if self.state:
            country_query = f'countries={country_code}&province={self.state}'
        else:
            country_query = f'countries={country_code}'

        return [
            f'{name_query}&{country_query}',
            f'{registered_number_query}&{country_query}'
        ]


class ReportInput(Model):
    creditsafe_id = StringType(required=True)


class CreditSafeSearchRequest(Model):
    is_demo = BooleanType(default=False)
    credentials = ModelType(CreditSafeCredentials, default=None)
    input_data = ModelType(SearchInput, required=True)

    def validate_credentials(self, data, value):
        if not self.is_demo and value is None:
            raise ValidationError('This field is required')


class CreditSafeCompanyReportRequest(Model):
    is_demo = BooleanType(default=False)
    credentials = ModelType(CreditSafeCredentials, default=None)
    input_data = ModelType(ReportInput, required=True)
