from enum import unique, Enum
from flask import abort, request
from functools import wraps

from schematics import Model
from schematics.exceptions import DataError
from schematics.types import ModelType, BooleanType, StringType


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
    credentials = ModelType(EquifaxCredentials, required=True)

    is_demo = BooleanType(default=False)
