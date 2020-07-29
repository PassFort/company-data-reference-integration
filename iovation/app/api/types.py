import pycountry
import logging

from datetime import datetime
from enum import unique, Enum
from flask import abort, g, request
from functools import wraps

from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types.serializable import serializable
from schematics.types import BooleanType, StringType, ModelType, ListType, UUIDType, IntType, DecimalType, DateType, FloatType

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


class IovationError(Exception):

    def __init__(self, response):
        self.response = response


class IovationCheckError(IovationError):
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
            'message': "Provider Error: {!r} while running 'Iovation' service.".format(provider_message),
            'info': {
               'provider': 'Iovation',
               'original_error': provider_message,
               'timestamp': str(datetime.now())
            }
        }

    @staticmethod
    def provider_misconfiguration_error(provider_message: str):
        return {
            'code': ErrorCode.MISCONFIGURATION_ERROR.value,
            'source': 'PROVIDER',
            'message': "Provider Configuration Error: {!r} while running 'Iovation' service".format(provider_message),
            'info': {
                'provider': 'Iovation',
                'original_error': provider_message,
                'timestamp': str(datetime.now())
            }
        }


class IovationCredentials(Model):
    subscriber_id = StringType(required=True)
    subscriber_account = StringType(required=True)
    password = StringType(required=True)
    use_test_environment = BooleanType(default=False)


class TransctionInsight(Model):
    billing_city = StringType(serialized_name="billingCity")
    billing_country = StringType(serialized_name="billingCountry")
    billing_postal_code = StringType(serialized_name="billingPostalCode")
    billing_region = StringType(serialized_name="billingRegion")
    billing_street = StringType(serialized_name="billingStreet")


class DeviceData(Model):
    account_code = StringType(serialized_name="accountCode")
    blackbox = StringType()
    stated_ip = StringType(serialized_name="statedIp")
    transaction_insight = ModelType(TransctionInsight, serialized_name="transactionInsight")
    type = StringType(required=True)


class DeviceMetadata(Model):
    token = StringType()
    stated_ip = StringType(default=None)
    action = StringType()
    reference_id = StringType(default=None)
    device_id = StringType(default=None)
    device_type = StringType(default=None)

    def as_iovation_device_data(self):
        return DeviceData({
            'account_code': self.reference_id,
            'blackbox': self.token,
            'stated_ip': self.stated_ip,
            'type': self.action,
        })


class StructuredAddress(Model):
    country = StringType(required=True)
    state_province = StringType(default=None)
    county = StringType(default=None)
    postal_code = StringType(default=None)
    locality = StringType(default=None)
    postal_town = StringType(default=None)
    route = StringType(default=None)
    street_number = StringType(default=None)
    premise = StringType(default=None)
    subpremise = StringType(default=None)
    address_lines = ListType(StringType(), default=None)


class AddressType(StringType):
    STRUCTURED = 'STRUCTURED'


class Address(StructuredAddress):
    type = AddressType(required=True, default=AddressType.STRUCTURED)
    original_freeform_address = StringType(default=None)
    original_structured_address = ModelType(StructuredAddress, default=None)


class ApproxDateType(DateType):
    formats = ['%Y-%m']


class DatedAddress(Model):
    address = ModelType(Address, required=True)
    start_date = ApproxDateType(default=None)
    end_date = ApproxDateType(default=None)

    def as_iovation_transaction_insight(self):
        country = None
        if self.address.country is not None:
            country_res = pycountry.countries.get(alpha_3=self.address.country)
            if country_res is not None:
                country = country_res.alpha_2

        return TransctionInsight({
            "billing_city": self.address.locality,
            "billing_country": country,
            "billing_postal_code": self.address.postal_code,
            "billing_region": self.address.state_province,
            "billing_street": self.address.route,
        })


class CheckInput(Model):
    address_history = ListType(ModelType(DatedAddress), default=None)
    device_metadata = ModelType(DeviceMetadata, required=True)

    def as_iovation_device_data(self):
        device_data = self.device_metadata.as_iovation_device_data()
        if self.address_history:
            device_data.transaction_insight = self.address_history[0].as_iovation_transaction_insight()
        return device_data


class IovationCheckRequest(Model):
    is_demo = BooleanType(default=False)
    credentials = ModelType(IovationCredentials, default=None)
    input_data = ModelType(CheckInput, required=True)

    def validate_credentials(self, data, value):
        if not self.is_demo and value is None:
            raise ValidationError('This field is required')


class IovationIpLocation(Model):
    city = StringType(default=None)
    country_code = StringType(serialized_name="countryCode", default=None)
    region = StringType(default=None)
    latitude = FloatType(min_value=-90, max_value=90)
    longitude = FloatType(min_value=-180, max_value=180)


class IpDetails(Model):
    address = StringType(default=None)
    ip_location = ModelType(IovationIpLocation, serialized_name="ipLocation", default=None)
    proxy = StringType(default=None)


class DeviceEntity(Model):
    type = StringType(default=None)
    alias = IntType(default=None)


class IovationDeviceFraudRule(Model):
    type = StringType()
    reason = StringType()
    score = IntType()

    def as_passfort_device_fraud_rule(self):
        return {
            'name': self.type,
            'reason': self.reason,
            'score': self.score
        }

class DeviceFraudRuleResults(Model):
    score = IntType(default=None)
    rules_matched = IntType(serialized_name="rulesMatched", default=None)
    rules = ListType(ModelType(IovationDeviceFraudRule), default=[])


class DeviceCheckDetails(Model):
    device = ModelType(DeviceEntity, default=None)
    real_ip = ModelType(IpDetails, serialized_name="realIp", default=None)
    rule_results = ModelType(DeviceFraudRuleResults, serialized_name="ruleResults", default=None)


class IovationOutput(Model):
    account_code = StringType(serialized_name="accountCode")
    details = ModelType(DeviceCheckDetails)
    id = UUIDType()
    reason = StringType()
    result = StringType(choices=["A", "D", "R"])
    stated_ip = StringType(serialized_name="statedIp")
    tracking_number = StringType(serialized_name="trackingNumber")

    @classmethod
    def from_json(cls, response):
        model = cls().import_data(response, apply_defaults=True)
        model.validate()

        return response, model


class Coordinates(Model):
    latitude = FloatType(min_value=-90, max_value=90)
    longitude = FloatType(min_value=-180, max_value=180)

class IPLocation(Model):
    ip_address = StringType()
    country = StringType()
    region = StringType()
    city = StringType()
    coordinates = ModelType(Coordinates)
    proxy = StringType()

IOVATION_PROXY_TO_PASSFORT = {
    # According to Iovation via e-mail ANONYMOUS Proxy
    # Is the only possible value.
    'ANONYMOUS PROXY': 'ANONYMOUS',
}

class DeviceFraudRule(Model):
    name = StringType()
    reason = StringType()
    score = IntType()


class DeviceFraudDetection(Model):
    provider_reference = StringType()
    recommendation = StringType()
    recommendation_reason = StringType()
    total_score = IntType()
    matched_rules = ListType(ModelType(DeviceFraudRule))


IOVATION_RECOMMENDATION_MAPPING = {
    'A': 'Allow',
    'D': 'Deny',
    'R': 'Review'
}


class IovationCheckResponse(Model):
    device_metadata = ModelType(DeviceMetadata)
    device_fraud_detection = ModelType(DeviceFraudDetection)
    ip_location = ModelType(IPLocation, serialize_when_none=False)

    @classmethod
    def from_iovation_output(cls, output, input_data):
        device_metadata = DeviceMetadata({
            'token': input_data.token,
            'stated_ip': output.stated_ip,
            'action': input_data.action,
            'reference_id': output.account_code
        })

        if output.details and output.details.device:
            device_metadata.device_id = output.details.device.alias
            device_metadata.device_type = output.details.device.type

        device_fraud_detection = DeviceFraudDetection({
            'provider_reference': output.tracking_number,
            'recommendation': IOVATION_RECOMMENDATION_MAPPING[output.result],
            'recommendation_reason': output.reason
        })

        if output.details and output.details.rule_results:
            device_fraud_detection.total_score = output.details.rule_results.score

            if len(output.details.rule_results.rules):
                matched_rules = []
                for rule in output.details.rule_results.rules:
                    matched_rules.append(rule.as_passfort_device_fraud_rule())
                device_fraud_detection.matched_rules = matched_rules

        if output.details and output.details.real_ip:
            ip_location = IPLocation()
            ip_location.ip_address = output.details.real_ip.address
            if output.details.real_ip.ip_location:
                real_ip_location = output.details.real_ip.ip_location
                if real_ip_location.country_code:
                    country = pycountry.countries.get(alpha_2=real_ip_location.country_code)
                    if country is not None:
                        ip_location.country = country.alpha_3
                    else:
                        logging.warning(f'Iovation sent unrecognised Real IP Country Code: {real_ip_location.country_code}')
                ip_location.region = output.details.real_ip.ip_location.region
                ip_location.city = output.details.real_ip.ip_location.city
                if real_ip_location.longitude and real_ip_location.latitude:
                    coords = Coordinates()
                    coords.longitude = real_ip_location.longitude
                    coords.latitude = real_ip_location.latitude
                    ip_location.coordinates = coords
            if output.details.real_ip.proxy:
                ip_location.proxy = IOVATION_PROXY_TO_PASSFORT.get(output.details.real_ip.proxy, output.details.real_ip.proxy)
            return cls({
                'device_metadata': device_metadata,
                'device_fraud_detection': device_fraud_detection,
                'ip_location': ip_location
            })

        return cls({
            'device_metadata': device_metadata,
            'device_fraud_detection': device_fraud_detection
        })
