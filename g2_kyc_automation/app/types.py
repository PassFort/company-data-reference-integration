import logging
from enum import Enum, unique
from schematics.common import NOT_NONE
from schematics.exceptions import ValidationError
from schematics.types.base import BooleanType, StringType, IntType
from schematics.types.compound import ModelType, ListType
from schematics import Model
from datetime import datetime
from flask import Response
from pycountry import countries


def country_alpha_3_to_2(alpha_3):
    try:
        return countries.get(alpha_3=alpha_3).alpha_2
    except (LookupError, AttributeError):
        logging.error(f"Received invalid alpha 3 code from PassFort {alpha_3}")
        return None


def clean_dict(dict):
    return {k: v for k, v in dict.items() if v is not None}


class MaybeBooleanType(BooleanType):
    def to_native(self, value, context=None):
        if isinstance(value, str):
            if value in self.TRUE_VALUES:
                value = True
            elif value in self.FALSE_VALUES:
                value = False

        elif isinstance(value, int) and value in [0, 1]:
            value = bool(value)

        if not isinstance(value, bool):
            # BooleanType impl would raise an error here
            # we just set the value to None
            # handles provider sending "null"
            value = None

        return value


class Credentials(Model):
    client_id = StringType(required=True)
    client_secret = StringType(required=True)


class Config(Model):
    use_sandbox = BooleanType(default=False)
    warn_zero_compass_score = BooleanType(default=False)
    compass_score_threshold = IntType(default=500)


class StructuredAddress(Model):
    type = StringType(required=True)
    country = StringType(required=True)
    locality = StringType(default=None)
    state_province = StringType(default=None)
    route = StringType(default=None)
    street_number = StringType(default=None)
    postal_code = StringType(default=None)

    class Options:
        export_level = NOT_NONE

    def validate_postal_code(self, data, value):
        if not (data.get('postal_code') or (data.get('locality') and data.get('state_province'))):
            raise ValidationError('Requires postal_code or state_province and locality!')
        return value

    def to_business_address(self):
        ser_data = self.to_primitive()

        return clean_dict({
            'country': country_alpha_3_to_2(ser_data['country']),
            'city': ser_data.get('locality'),
            'postcode': ser_data.get('postal_code'),
            'state': ser_data.get('state_province'),
            'street': ser_data.get('route'),
            'street_2': ser_data.get('street_number'),
        })


class CompanyAddress(Model):
    address = ModelType(StructuredAddress, required=True)
    type = StringType(required=True)


class ContactDetails(Model):
    url = StringType(required=True)


class CompanyMetadata(Model):
    name = StringType(required=True)
    contact_details: ContactDetails = ModelType(ContactDetails, required=True)
    addresses = ListType(ModelType(CompanyAddress), min_size=1, required=True)

    @property
    def address(self):
        return self.addresses[0].address

    @property
    def url(self):
        return self.contact_details.url


class CompanyData(Model):
    entity_type: str = StringType(required=True)
    metadata: CompanyMetadata = ModelType(CompanyMetadata, required=True)
    customer_ref: str = StringType(default=None)

    def as_request(self):
        request = {
            "company_name": self.metadata.name,
            "url": self.metadata.url,
            "business_address": self.metadata.address.to_business_address(),
        }

        if self.customer_ref is not None:
            return {
                **request,
                "vendor_id": self.customer_ref,
            }
        else:
            return request


class ReasonCode(Model):
    code: str = StringType(required=True)
    description: str = StringType(required=True)


class G2CompassResult(Model):
    compass_score = IntType(required=True)
    reason_codes = ListType(ModelType(ReasonCode), default=[])
    site_active = MaybeBooleanType(default=None)
    valid_url = MaybeBooleanType(default=None)
    request_id = StringType(required=True)

    class Options:
        export_level = NOT_NONE


class Messages(Model):
    crit = ListType(StringType(), default=[])
    warn = ListType(StringType(), default=[])
    info = ListType(StringType(), default=[])
    ok = ListType(StringType(), default=[])

    def get_joined(self):
        def build_messages(level, msgs):
            return [{
                'level': level,
                'description': msg
            } for msg in msgs]

        critical = build_messages('CRITICAL', self.crit)
        warn = build_messages('WARNING', self.warn)
        info = build_messages('INFO', self.info)
        ok = build_messages('OK', self.ok)

        return critical + warn + info + ok


class G2Report(Model):
    g2_compass_results = ListType(ModelType(G2CompassResult))
    pdf_url: str = StringType(required=True)
    messages: Messages = ModelType(Messages, required=True, default={})
    test = StringType(required=True)

    @property
    def compass_result(self):
        return self.g2_compass_results[0]

    def to_passfort(self):
        messages = self.messages.get_joined()
        reason_codes = [{
            "name": x.code,
            "value": x.description
        } for x in self.compass_result.reason_codes]

        ser_compass_result = self.compass_result.to_primitive()

        return {
            "g2_compass_score": {
                "score": ser_compass_result['compass_score'],
                "reason_codes": reason_codes,
                "request_id": ser_compass_result.get('request_id'),
            },
            "messages": messages,
            "pdf_url": self.pdf_url,
            "valid_url": ser_compass_result.get('valid_url'),
            "is_active": ser_compass_result.get('site_active'),
        }


@unique
class ErrorCode(Enum):
    INVALID_INPUT_DATA = 201
    PROVIDER_MISCONFIGURATION_ERROR = 205
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303
    UNKNOWN_INTERNAL_ERROR = 401


class G2Exception(Exception):
    def __init__(self, response: Response):
        self.response = response


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
            'message': 'Connection error when contacting G2',
            'info': {
                'raw': '{}'.format(e)
            }
        }

    @staticmethod
    def provider_misconfiguration_error(e):
        return {
            'code': ErrorCode.PROVIDER_MISCONFIGURATION_ERROR.value,
            'source': 'PROVIDER',
            'message': f"Provider Configuration Error: '{e}' while running the 'G2' service",
            'info': {
                "Provider": "G2",
                "Timestamp": str(datetime.now())
            }
        }

    @staticmethod
    def provider_unknown_error(e, extra=None):
        return {
            'code': ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
            'source': 'PROVIDER',
            'message': e or 'There was an error calling G2',
            'info': {
                'Provider': 'G2',
                'Timestamp': str(datetime.now()),
                'Extra': extra,
            }
        }

    @staticmethod
    def from_exception(e):
        return {
            'code': ErrorCode.UNKNOWN_INTERNAL_ERROR.value,
            'source': 'ENGINE',
            'message': '{}'.format(e)
        }


class RequestBase(Model):
    credentials: Credentials = ModelType(Credentials, required=True)
    config: Config = ModelType(Config, required=True)
    is_demo: bool = BooleanType(default=False)

    @property
    def client_setup(self):
        return {
            "client_id": self.credentials.client_id,
            "client_secret": self.credentials.client_secret,
            "use_sandbox": self.config.use_sandbox,
            "is_demo": self.is_demo
        }


class CaseIdInput(Model):
    case_id = StringType(required=True)


class ScreeningRequest(RequestBase):
    input_data = ModelType(CompanyData, required=True)


class PollRequest(RequestBase):
    input_data = ModelType(CaseIdInput, required=True)


class ReportRequest(RequestBase):
    input_data = ModelType(CaseIdInput, required=True)
