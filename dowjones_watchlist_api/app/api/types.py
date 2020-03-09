import logging
from enum import unique, Enum
from functools import wraps

from flask import (
    abort,
    g,
    request,
)
from schematics import Model
from schematics.common import NOT_NONE
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


@unique
class Gender(Enum):
    M = 'M'
    F = 'F'

    def from_dowjones(string):
        if string.lower() == 'male':
            return Gender.M
        elif string.lower() == 'female':
            return Gender.F
        else:
            return None


@unique
class CountryMatchType(Enum):
    AFFILIATION = 'AFFILIATION'
    CITIZENSHIP = 'CITIZENSHIP'
    CURRENT_OWNERSHIP = 'CURRENT_OWNERSHIP'
    OWNERSHIP = 'OWNERSHIP'
    JURISDICTION = 'JURISDICTION'
    REGISTRATION = 'REGISTRATION'
    ALLEGATION = 'ALLEGATION'
    RESIDENCE = 'RESIDENCE'
    RISK = 'RISK'
    FORMERLY_SANCTIONED = 'FORMERLY_SANCTIONED'
    SANCTIONED = 'SANCTIONED'
    UNKNOWN = 'UNKNOWN'

    def from_dowjones(label):
        '''Map from DJ's country match type onto ours

        DJ's docs provide a list of the possible match types but they
        appear to differ in format from what's actually returned from
        the API.

        E.g. The docs say `Country of Jurisdiction` but the
        `country-type` attribute actually returned is just
        `Jurisdiction`.

        As a result, we try and be as accepting as possible.
        '''
        if label is None:
            return CountryMatchType.UKNOWN
        
        lowered_label = label.lower()
        if 'affiliation' in lowered_label:
            return CountryMatchType.AFFILIATION
        elif 'citizenship' in lowered_label:
            return CountryMatchType.CITIZENSHIP
        elif 'ownership' in lowered_label:
            if 'current' in lowered_label:
                return CountryMatchType.CURRENT_OWNERSHIP
            else:
                return CountryMatchType.OWNERSHIP
        elif 'jurisdiction' in lowered_label:
            return CountryMatchType.JURISDICTION
        elif 'registration' in lowered_label:
            return CountryMatchType.REGISTRATION
        elif 'allegation' in lowered_label:
            return CountryMatchType.ALLEGATION
        elif 'residence' in lowered_label or 'resident' in lowered_label:
            return CountryMatchType.RESIDENCE
        elif 'risk' in lowered_label:
            return CountryMatchType.RISK
        elif 'sanction' in lowered_label:
            if 'former' in lowered_label:
                return CountryMatchType.FORMERLY_SANCTIONED
            else:
                return CountryMatchType.SANCTIONED
        else:
            logging.error(f'Unmatched country match type {label}')
            return CountryMatchType.UNKNOWN


class MatchEvent(Model):
    event_type = StringType(required=True, choices=[ty.value for ty in MatchEventType])
    match_id = StringType(required=True)
    provider_name = StringType(required=True)

    # Match information
    match_name = StringType()
    score = FloatType()
    match_custom_label = StringType()
    match_countries = ListType(StringType())
    country_match_types = ListType(StringType(choices=[ty.value for ty in CountryMatchType]))

    # Additional information
    gender = StringType(choices=[gender.value for gender in Gender])
    deceased = BooleanType()

    class Options:
        export_level = NOT_NONE


class ScreeningResponse(Model):
    errors = ListType(ModelType(Error), default=[])
    events = ListType(ModelType(MatchEvent), default=[])


class TestError(Model):
    name = IntType()
