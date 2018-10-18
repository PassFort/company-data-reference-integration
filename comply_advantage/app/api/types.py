from flask import abort, g, request
from enum import unique, Enum
from functools import wraps
from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, ListType, DateType, DecimalType, CompoundType
from schematics.exceptions import DataError, ValidationError


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


class ComplyAdvantageCredentials(Model):
    api_key = StringType(required=True)

    @property
    def base_url(self):
        return "https://api.complyadvantage.com/"


class ComplyAdvantageConfig(Model):
    fuzziness = DecimalType(min_value=0.0, max_value=1.0, default=0.5)
    enable_ongoing_monitoring = BooleanType(default=False)
    include_adverse_media = BooleanType(default=False)


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)

    def combine(self):
        return ' '.join(self.given_names + [self.family_name])


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    dob = DateType(default=None, formats=['%Y', '%Y-%m', '%Y-%m-%d'])


class CompanyMetadata(Model):
    name = StringType(required=True)
    country_of_incorporation = StringType(default=None)


class MatchEvent(Model):
    event_type = StringType(required=True, choices=['PEP_FLAG', 'SANCTION_FLAG', 'REFER_FLAG'])
    match_id = StringType(required=True)

    provider_name = StringType()

    # Match information
    match_name = StringType()
    match_dates = ListType(DateType)

    # Additional information
    aliases = ListType(StringType)

    def as_validated_json(self):
        self.validate()
        return self.to_primitive()


class ReferMatchEvent(MatchEvent):
    event_type = StringType(required=True, choices=['REFER_FLAG'], default='REFER_FLAG')

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get('event_type') == 'REFER_FLAG'

    class Options:
        serialize_when_none = False


class ScreeningRequestData(Model):
    entity_type = StringType(choices=['INDIVIDUAL', 'COMPANY'], required=True)
    metadata = ModelType(CompanyMetadata, default=None)
    personal_details = ModelType(PersonalDetails, default=None)

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
    def search_term(self):
        raise NotImplementedError()

    @property
    def comply_advantage_entity_type(self):
        if self.entity_type == 'INDIVIDUAL':
            return 'person'
        else:
            return 'company'

    @property
    def search_term(self):
        if self.entity_type == 'INDIVIDUAL':
            return self.personal_details.name.combine()
        return self.metadata.name

    def to_provider_format(self, config: ComplyAdvantageConfig):
        type_filter = ["pep", "sanction"]

        if config.include_adverse_media:
            type_filter = type_filter + ["adverse-media", "warning", "fitness-probity"]

        base_format = {
            "search_term": self.search_term,
            "fuzziness": config.fuzziness,
            "filters": {
                "entity_type": self.comply_advantage_entity_type,
                "types": type_filter
            }
        }
        if self.entity_type == 'INDIVIDUAL':
            if self.personal_details.dob:
                base_format['filters']['birth_year'] = self.personal_details.dob.year
        return base_format

    class Options:
        serialize_when_none = False


class ScreeningRequest(Model):
    config = ModelType(ComplyAdvantageConfig, required=True)
    credentials = ModelType(ComplyAdvantageCredentials, required=True)

    input_data = ModelType(ScreeningRequestData, required=True)

    is_demo = BooleanType(default=False)
