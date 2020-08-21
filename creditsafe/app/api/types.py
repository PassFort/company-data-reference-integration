import pycountry

from datetime import datetime
from enum import unique, Enum
from flask import abort, g, request
from functools import wraps
from typing import List
from urllib.parse import quote_plus

from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types.serializable import serializable
from schematics.types import BooleanType, StringType, ModelType, ListType, UUIDType, IntType, DecimalType, DateType, \
    UTCDateTimeType, BaseType

from .event_mappings import MonitoringConfigType


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


class CreditSafeMonitoringError(CreditSafeError):
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


# These countries cause creditsafe to error with error (" exact")
# when doing an exact search
NO_EXACT_SEARCH_COUNTRIES = [
    'AE',
    'AU',
    'BG',
    'CN',
    'CZ',
    'EE',
    'HK',
    'HU',
    'IN',
    'JP',
    'KZ'
    'NZ',
    'PT',
    'RO',
    'RU',
    'SE',
    'SG',
    'SI',
    'US',
    'ZA',
]


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

    @property
    def supports_state(self):
        return self.country in {
            'USA', 'CAN'
        }

    def build_queries(self):
        country_code = self.get_creditsafe_country()
        all_queries = []
        any_queries = []
        all_queries.append(f'countries={country_code}')

        if self.supports_state and self.state:
            # Only supports state and name search, not state and number
            if self.name:
                any_queries.append(f'name={quote_plus(self.name)}&province={quote_plus(self.state)}')
            elif self.query:
                any_queries.append(f'name={quote_plus(self.query)}&province={quote_plus(self.state)}')
        else:
            if self.name:
                any_queries.append(f'name={quote_plus(self.name)}')
            elif self.query:
                any_queries.append(f'name={quote_plus(self.query)}')
        exact_search = '' if country_code in NO_EXACT_SEARCH_COUNTRIES else '&exact=True'
        if self.number:
            any_queries.append(f'regNo={quote_plus(self.number)}{exact_search}')
        elif self.query:
            any_queries.append(f'regNo={quote_plus(self.query)}{exact_search}')

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


class CreditSafePortfolioRequest(Model):
    credentials = ModelType(CreditSafeCredentials, default=None)
    portfolio_name = StringType(required=True)


class CreditSafeMonitoringRequest(Model):
    credentials = ModelType(CreditSafeCredentials, default=None)
    portfolio_id = IntType(required=True)
    creditsafe_id = StringType(required=True)


class MonitoringConfig(Model):
    last_run_date = UTCDateTimeType()
    institution_config_id = UUIDType(required=True)
    portfolio_id = IntType(required=True)


class CreditSafeMonitoringEventsRequest(Model):
    credentials = ModelType(CreditSafeCredentials, default=None)
    monitoring_configs = ListType(ModelType(MonitoringConfig))
    callback_url = StringType(required=True, default=None)


class MonitoringEvent(Model):
    creditsafe_id = StringType(required=True)
    event_type = StringType(required=True, choices=[event_type.value for event_type in MonitoringConfigType])
    event_date = StringType()
    rule_code = IntType()


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


class MonetaryValue(Model):
    currency_code = StringType(default=None)
    value = DecimalType(required=True)

    @serializable(serialized_name="value")
    def value_out(self):
        return float(self.value)

    class Options:
        serialize_when_none = False


def to_passfort_datetime_format(utc):
    return utc.strftime("%Y-%m-%d %H:%M:%S")


class Rating(Model):
    value = StringType(required=True)
    description = StringType(default=None)

    class Options:
        serialize_when_none = False


class CreditChangeEntry(Model):
    date = UTCDateTimeType(default=None)
    credit_limit = ModelType(MonetaryValue, default=None)
    credit_rating = ModelType(Rating, default=None)
    international_rating = ModelType(Rating, default=None)

    @serializable(serialized_name="date")
    def date_out(self):
        # This seems to be called even when the field is None, despite
        # serialize_when_none being set False below
        if self.date is None:
            return None
        else:
            return to_passfort_datetime_format(self.date)

    class Options:
        serialize_when_none = False


class StatementValue(Model):
    value = BaseType(default=None)
    currency_code = StringType(default=None)

    class Options:
        serialize_when_none = False


class StatementEntryBase(Model):
    name = StringType(required=True)
    value = ModelType(StatementValue, default=None)
    value_type = StringType(choices=['CURRENCY', 'NUMBER', 'PERCENTAGE'])
    yoy = DecimalType(default=None)

    @serializable(serialized_name="yoy")
    def yoy_out(self):
        if self.yoy is not None:
            return float(self.yoy)

    class Options:
        serialize_when_none = False


class StatementEntry(StatementEntryBase):
    group_name = StringType(default=None)

    class Options:
        serialize_when_none = False


class StatementEntryGroup(StatementEntryBase):
    pass


class Statement(Model):
    statement_type = StringType(required=True, choices=[
        'PROFIT_AND_LOSS', 'BALANCE_SHEET', 'CAPITAL_AND_RESERVES', 'OTHER_FINANCIAL_ITEMS', 'CASH_FLOW'])
    statement_format = StringType(required=True)
    currency_code = StringType(default=None)
    date = UTCDateTimeType(required=True)  # (Y-M-D, Y-M, or Y)
    groups = ListType(ModelType(StatementEntryGroup), default=[])
    entries = ListType(ModelType(StatementEntry), default=[])

    @serializable(serialized_name="date")
    def date_out(self):
        return self.date and self.date.strftime("%Y-%m-%d")


class Financials(Model):
    credit_history = ListType(ModelType(CreditChangeEntry), default=[])
    contract_limit = ModelType(MonetaryValue, default=None)
    statements = ListType(ModelType(Statement), default=[])

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
    title = StringType(default=None)
    given_names = ListType(StringType, required=True)
    family_name = StringType(required=True, min_length=1)

    class Options:
        serialize_when_none = False


class PersonalDetails(Model):
    name = ModelType(FullName, required=True)
    dob = StringType(default=None)
    nationality = StringType(default=None)

    def merge(self, other: 'PersonalDetails'):
        if self.dob is None or (other.dob and (len(self.dob) < len(other.dob))):
            self.dob = other.dob
        if self.nationality is None:
            self.nationality = other.nationality

        if self.name.title is None:
            self.name.title = other.name.title

    class Options:
        serialize_when_none = False


class CompanyMetadata(Model):
    name = StringType(required=True)
    country_of_incorporation = StringType(default=None)
    state_of_incorporation = StringType(default=None)
    number = StringType(default=None)
    creditsafe_id = StringType(default=None)

    def merge(self, other: 'CompanyMetadata'):
        if self.country_of_incorporation is None:
            self.country_of_incorporation = other.country_of_incorporation
        if self.state_of_incorporation is None:
            self.state_of_incorporation = other.state_of_incorporation
        if self.number is None:
            self.number = other.number
        if self.creditsafe_id is None:
            self.creditsafe_id = other.creditsafe_id

    class Options:
        serialize_when_none = False


class EntityData(Model):
    personal_details = ModelType(PersonalDetails, default=None)
    metadata = ModelType(CompanyMetadata, default=None)
    entity_type = StringType(required=True)

    @classmethod
    def as_individual(cls, first_names, last_name, dob, nationality=None, title=None):
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
                    'title': title,
                    'given_names': first_names,
                    'family_name': last_name
                },
                'dob': dob_str,
                'nationality': nationality
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

    def merge(self, other: 'EntityData'):
        if self.personal_details:
            self.personal_details.merge(other.personal_details)
        elif self.metadata:
            self.metadata.merge(other.metadata)

    class Options:
        serialize_when_none = False


class BaseRelationship(Model):
    relationship_type = StringType(required=True, choices=["OFFICER", "SHAREHOLDER"])
    associated_role = StringType(
        required=True,
        choices=[
            "DIRECTOR",
            "COMPANY_SECRETARY",
            "SHAREHOLDER",
            "BENEFICIAL_OWNER",
            "PARTNER",
            "OTHER"
        ])  # The only choices supported by this integration

    is_active = BooleanType(required=True)


class PassFortAssociate(Model):
    associate_id = UUIDType(default=None)
    entity_type = StringType(required=True)
    immediate_data = ModelType(EntityData, required=True)
    relationships = ListType(ModelType(BaseRelationship), required=True)

    @serializable
    def provider_name(self):
        return 'Creditsafe'

    class Options:
        serialize_when_none = False

    def merge(self, other: 'PassFortAssociate') -> ():
        if self.entity_type != other.entity_type:
            raise AssertionError('attempting to merge different entity types')

        self.immediate_data.merge(other.immediate_data)
        # UI can't display this properly. don;t merge beneficial owner relationships if shareholder ones exist
        if not(any(r.associated_role == 'SHAREHOLDER' for r in self.relationships) and
               any(r.associated_role == 'BENEFICIAL_OWNER' for r in other.relationships)):
            self.relationships.extend(other.relationships)


class OfficerRelationship(BaseRelationship):
    original_role = StringType(default=None, serialize_when_none=False)
    appointed_on = DateType(default=None, serialize_when_none=False)

    @serializable
    def relationship_type(self):
        return 'OFFICER'

    class Options:
        serialize_when_none = False


class PassFortShareholding(Model):
    share_class = StringType(default=None)
    currency = StringType(default=None)
    amount = IntType(default=None)
    percentage = DecimalType(default=None)

    @serializable(serialized_name="percentage")
    def percentage_out(self):
        return float(self.percentage) if self.percentage is not None else None

    @serializable
    def provider_name(self):
        return 'Creditsafe'

    class Options:
        serialize_when_none = False


class ShareholderRelationship(BaseRelationship):
    shareholdings = ListType(ModelType(PassFortShareholding), required=True)

    @serializable
    def total_percentage(self):
        return float(sum(x.percentage for x in self.shareholdings if x.percentage is not None))

    @serializable
    def relationship_type(self):
        return 'SHAREHOLDER'

    class Options:
        serialize_when_none = False


class BeneficialOwnerRelationship(BaseRelationship):

    @serializable
    def relationship_type(self):
        return 'SHAREHOLDER'

    class Options:
        serialize_when_none = False
