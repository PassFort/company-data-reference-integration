from enum import unique, Enum
from functools import wraps

from flask import (
    abort,
    g,
    request,
)
from schematics import Model
from schematics.types import (
    BaseType,
    BooleanType,
    DictType,
    IntType,
    ListType,
    StringType,
    ModelType,
    FloatType,
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
                abort(400, e.to_primitive())
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


@unique
class ErrorSource(Enum):
    API = 'API'


class Error(Model):
    code = IntType(required=True, choices=[code.value for code in ErrorCode])
    source = StringType(required=True, choices=[source.value for source in ErrorSource])
    message = StringType(required=True)
    info = BaseType()

    def from_exception(e):
        return {
            'code': ErrorCode.UNKNOWN_INTERNAL_ERROR.value,
            'source': 'ENGINE',
            'message': '{}'.format(e)
        }

    @staticmethod
    def bad_api_request(e):
        return Error({
            'code': ErrorCode.INVALID_INPUT_DATA.value,
            'source': 'API',
            'message': 'Bad API request',
            'info': e
        })


@unique
class MatchEventType(Enum):
    PEP_FLAG = 'PEP_FLAG'
    SANCTION_FLAG = 'SANCTION_FLAG'
    ADVERSE_MEDIA_FLAG = "ADVERSE_MEDIA_FLAG"
    REFER_FLAG = 'REFER_FLAG'

    def from_risk_icon(icon):
        import logging

        if icon == 'AM':
            return MatchEventType.ADVERSE_MEDIA_FLAG
        elif icon == 'PEP':
            return MatchEventType.PEP_FLAG
        elif icon == 'SAN':
            return MatchEventType.SANCTION_FLAG
        elif icon.startswith('SI'):
            return MatchEventType.ADVERSE_MEDIA_FLAG
        else:
            return MatchEventType.REFER_FLAG


class MatchEvent(Model):
    event_type = StringType(required=True, choices=[ty.value for ty in MatchEventType])
    match_id = StringType(required=True)
    provider_name = StringType(required=True)

    match_name = StringType()
    score = FloatType()


class ScreeningResponse(Model):
    errors = ListType(ModelType(Error), default=[])
    events = ListType(ModelType(MatchEvent), default=[])


class TestError(Model):
    name = IntType()
