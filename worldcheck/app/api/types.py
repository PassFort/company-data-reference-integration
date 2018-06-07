from flask import abort, g, request
from enum import unique, Enum
from functools import wraps
from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, DateType
from schematics.exceptions import DataError, ValidationError

from swagger_client.rest import ApiException
from swagger_client.models import MatchStrength


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
                model.validate(partial=True)
            except DataError as e:
                abort(400, Error.bad_api_request(e))

            return fn(model, *args, **kwargs)

        return wrapped_fn

    return validates_model


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201

    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303

    UNKNOWN_INTERNAL_ERROR = 401


class Error:

    @staticmethod
    def from_provider_exception(e: ApiException):
        """
        Possible provider errors:

        400 Bad request.

        < Error > array

        ---------------

        401 The request has failed an authorisation check.
        This can happen for a variety of reasons, such as an invalid or expired API key,
        an invalid HMAC signature or a request timing issue/problem with the Date header value.
        The API client should ensure a correctly synchronised clock is used to generate request timestamps.

        No Content

        ---------------

        404 Cannot return response

        < Error > array

        ---------------

        415 For requests with payloads, an unsupported Content-Type was specified.
        The World-Check One API only supports a content type of application/json.

        No Content

        ---------------

        429

        The API client is making too many concurrent requests, and some are being throttled.
        Throttled requests can be retried (with an updated request Date and HTTP signature) after a short delay.

        No Content

        ---------------

        500 Unexpected error

        < Error > array

        """
        message = {
            '400': 'Bad request submitted to World Check',
            '401': 'The request has failed an authorisation check',
            '404': 'The provider cannot return a response for the specified id',
            '415': 'An unsupported Content-Type was specified',
            '429': 'The API client is making too many concurrent requests, and some are being throttled',
            '500': 'Provider unexpected error'
        }.get(str(e.status), 'Provider unhandled error')
        if e.body and e.body != '[]':
            message = message + ': ' + str(e.body)
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': message
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


class WorldCheckCredentials(Model):
    is_pilot = BooleanType(default=False)
    api_key = StringType(required=True)
    api_secret = StringType(required=True)
    base_url = StringType(default='/v1')

    @property
    def url(self):
        if self['is_pilot']:
            return 'rms-world-check-one-api-pilot.thomsonreuters.com'
        else:
            return 'rms-world-check-one-api.thomsonreuters.com'


class WorldCheckConfig(Model):
    group_id = StringType(required=True)
    minimum_match_strength = StringType(
        choices=[
            MatchStrength.WEAK, MatchStrength.MEDIUM, MatchStrength.STRONG, MatchStrength.EXACT
        ],
        default=MatchStrength.WEAK
    )


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)

    def combine(self):
        return ' '.join(self.given_names + [self.family_name])


class Country(Model):
    v = StringType(default=None)


class Gender(Model):
    v = StringType(choices=["M", "F"], default=None)

    @property
    def wordlcheck_gender(self):
        if self.v is None:
            return None
        if self.v == "M":
            return "MALE"
        if self.v == "F":
            return "FEMALE"
        raise NotImplementedError()


class TaggedString(Model):
    v = StringType(default=None)


class TaggedDate(Model):
    v = DateType(default=None)


class TaggedFullName(Model):
    v = ModelType(FullName, required=True)


class PersonalDetails(Model):
    name = ModelType(TaggedFullName, required=True)
    dob = ModelType(TaggedDate, default=None)
    gender = ModelType(Gender, default=None)
    nationality = ModelType(Country, default=None)


class CompanyMetadata(Model):
    name = ModelType(TaggedString, required=True)
    country_of_incorporation = ModelType(Country, default=None)


class WorldCheckRefs(Model):
    worldcheck_system_id = StringType


class ScreeningRequestData(Model):
    entity_type = StringType(choices=['INDIVIDUAL', 'COMPANY'], required=True)

    personal_details = ModelType(PersonalDetails, default=None)
    metadata = ModelType(CompanyMetadata, default=None)

    def validate_personal_details(self, data, value):
        if 'entity_type' not in data:
            return value

        if data['entity_type'] == 'INDIVIDUAL' and not value:
            raise ValidationError('Personal details are required for individuals')
        return value

    def validate_metadata(self, data, value):
        if 'entity_type' not in data:
            return value

        if data['entity_type'] == 'COMPANY' and not value:
            raise ValidationError('Company metadata is required for companies')
        return value

    @property
    def name(self):
        if self.entity_type == 'INDIVIDUAL':
            return self.personal_details.name.v.combine()
        else:
            return self.metadata.name.v

    @property
    def worldcheck_entity_type(self):
        from swagger_client.models.case_entity_type import CaseEntityType
        if self.entity_type == 'INDIVIDUAL':
            return CaseEntityType.INDIVIDUAL
        elif self.entity_type == 'COMPANY':
            return CaseEntityType.ORGANISATION

        raise NotImplementedError()


class ScreeningRequest(Model):
    config = ModelType(WorldCheckConfig, required=True)
    credentials = ModelType(WorldCheckCredentials, required=True)

    input_data = ModelType(ScreeningRequestData, required=True)
    is_demo = BooleanType(default=False)


class ScreeningResultsRequest(Model):
    credentials = ModelType(WorldCheckCredentials, required=True)
    config = ModelType(WorldCheckConfig, default=None)
    is_demo = BooleanType(default=False)
