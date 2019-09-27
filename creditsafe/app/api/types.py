import pycountry

from datetime import datetime
from enum import unique, Enum
from flask import abort, g, request
from functools import wraps
from urllib.parse import quote_plus

from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types.serializable import serializable
from schematics.types import BooleanType, StringType, ModelType, ListType, UUIDType, IntType, DecimalType, DateType

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
            'message': "Provider Error: {!r} while running 'Creditsafe' service.".format(provider_message),
            'info': {
               'provider': 'Creditsafe',
               'original_error': provider_message,
               'timestamp': str(datetime.now())
            }
        }

    @staticmethod
    def provider_misconfiguration_error(provider_message: str):
        return {
            'code': ErrorCode.MISCONFIGURATION_ERROR.value,
            'source': 'PROVIDER',
            'message': "Provider Configuration Error: {!r} while running 'Creditsafe' service".format(provider_message),
            'info': {
                'provider': 'Creditsafe',
                'original_error': provider_message,
                'timestamp': str(datetime.now())
            }
        }


class CreditSafeCredentials(Model):
    username = StringType(required=True)
    password = StringType(required=True)


class SearchInput(Model):
    # Name or company number
    query = StringType(default=None)
    name = StringType(default=None)
    number = StringType(default=None)
    country = StringType(required=True, choices=[c.alpha_3 for c in pycountry.countries])
    state = StringType(default=None)

    def get_creditsafe_country(self):
        country = pycountry.countries.get(alpha_3=self.country)
        return country.alpha_2

    def build_queries(self):
        country_code = self.get_creditsafe_country()

        all_queries = []
        any_queries = []
        all_queries.append(f'countries={country_code}')
        if self.state:
            all_queries.append(f'province={quote_plus(self.state)}')

        if self.name:
            any_queries.append(f'name={quote_plus(self.name)}')
        elif self.query:
            any_queries.append(f'name={quote_plus(self.query)}')

        if self.number:
            any_queries.append(f'regNo={quote_plus(self.number)}&exact=True')
        elif self.query:
            any_queries.append(f'regNo={quote_plus(self.query)}&exact=True')

        return ['&'.join(all_queries + [any_query]) for any_query in any_queries]


class ReportInput(Model):
    creditsafe_id = StringType(required=True)
    country_of_incorporation = StringType(default=None)


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


class PassFortFreeformAddress(Model):
    text = StringType(required=True)
    country = StringType(default=None)

    @serializable
    def type(self):
        return 'FREEFORM'

    class Options:
        serialize_when_none = False


class PassFortAddress(Model):
    type = StringType(default=None, serialize_when_none=False)
    address = ModelType(PassFortFreeformAddress, required=True)


class PassFortStructuredCompanyType(Model):
    is_limited = BooleanType(default=None)
    is_public = BooleanType(default=None)
    ownership_type = StringType(default=None)

    class Options:
        serialize_when_none = False


class PassFortMetadata(Model):
    name = StringType(required=True)
    number = StringType(required=True)
    addresses = ListType(ModelType(PassFortAddress), required=True)
    country_of_incorporation = StringType(default=None)
    is_active = BooleanType(default=None)
    incorporation_date = DateType(default=None)
    company_type = StringType(default=None)
    structured_company_type = ModelType(PassFortStructuredCompanyType, default=None)

    class Options:
        serialize_when_none = False


class FullName(Model):
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    dob = StringType(default=None)

    class Options:
        serialize_when_none = False


class CompanyMetadata(Model):
    name = StringType(required=True)
    country_of_incorporation = StringType(default=None)
    state_of_incorporation = StringType(default=None)
    number = StringType(default=None)
    creditsafe_id = StringType(default=None)

    class Options:
        serialize_when_none = False

class EntityData(Model):
    personal_details = ModelType(PersonalDetails, default=None)
    metadata = ModelType(CompanyMetadata, default=None)
    entity_type = StringType(required=True)

    @classmethod
    def as_individual(cls, first_names, last_name, dob):
        if dob:
            if dob.day == 1:
                dob_str = dob.strftime("%Y-%m")
            else:
                dob_str = dob.strftime("%Y-%m-%d")
        else:
            dob_str = None
        return cls({
            'personal_details': {
                'name': {
                    'given_names': first_names,
                    'family_name': last_name
                },
                'dob': dob_str
            },
            'entity_type': 'INDIVIDUAL'
        })

    @classmethod
    def as_company(cls, last_name, search_data):
        metadata = {}
        if search_data:
            metadata = search_data
        metadata['name'] = last_name
        return cls({
            'metadata': metadata,
            'entity_type': 'COMPANY'
        })

    class Options:
        serialize_when_none = False

class PassFortAssociate(Model):
    resolver_id = UUIDType(default=None)
    entity_type = StringType(required=True)
    immediate_data = ModelType(EntityData, required=True)

    @serializable
    def provider_name(self):
        return 'CreditSafe'

    class Options:
        serialize_when_none = False

class PassFortOfficer(PassFortAssociate):
    original_role = StringType(default=None, serialize_when_none=False)
    appointed_on = DateType(default=None, serialize_when_none=False)

    class Options:
        serialize_when_none = False


class PassFortShareholding(Model):
    share_class = StringType(default=None)
    currency = StringType(default=None)
    amount = IntType(default=None)
    percentage = DecimalType(required=True)

    @serializable(serialized_name="percentage")
    def percentage_out(self):
        return float(self.percentage)

    @serializable
    def provider_name(self):
        return 'CreditSafe'

    class Options:
        serialize_when_none = False


class PassFortShareholder(PassFortAssociate):
    shareholdings = ListType(ModelType(PassFortShareholding), required=True)

    @serializable
    def total_percentage(self):
        return float(sum(x.percentage for x in self.shareholdings))

    class Options:
        serialize_when_none = False
