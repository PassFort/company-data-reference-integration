from enum import unique, Enum
from functools import wraps

from flask import (
    abort,
    g,
    request,
)
from schematics import Model
from schematics.types import (
    BooleanType,
    ListType,
    StringType,
    ModelType,
)
from schematics.exceptions import (
    DataError,
    ValidationError,
)


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


class WatchlistAPICredentials(Model):
    namespace = StringType(required=True)
    username = StringType(required=True)
    password = StringType(required=True)
    url = StringType(required=True)


class WatchlistAPIConfig(Model):
    pass


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    dob = StringType(default=None)
    nationality = StringType(default=None)


class InputData(Model):
    entity_type = StringType(choices=['INDIVIDUAL'], required=True)
    personal_details = ModelType(PersonalDetails, required=True)


class ScreeningRequest(Model):
    config = ModelType(WatchlistAPIConfig, required=True)
    credentials = ModelType(WatchlistAPICredentials, required=True)
    input_data = ModelType(InputData, required=True)
    is_demo = BooleanType(default=False)


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
