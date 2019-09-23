import pycountry

from enum import unique, Enum
from flask import abort, g, request
from functools import wraps

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
            'message': 'Provider unhandled error',
            'info': {
                'provider_error': {
                    'message': provider_message
                }
            }
        }


class IovationCredentials(Model):
    subscriber_id = StringType(required=True)
    subscriber_account = StringType(required=True)
    password = StringType(required=True)


class DeviceData(Model):
    account_code = StringType(serialized_name="accountCode")
    blackbox = StringType()
    statedip = StringType()
    type = StringType(required=True)


class DeviceMetadata(Model):
    token = StringType()
    stated_ip = StringType()
    action = StringType()
    reference_id = StringType()
    device_id = StringType()
    device_type = StringType()

    def as_iovation_device_data(self):
        return DeviceData({
            'account_code': self.reference_id,
            'blackbox': self.token,
            'statedip': self.stated_ip,
            'type': self.action
        })


class CheckInput(Model):
    device_metadata = ModelType(DeviceMetadata, required=True)


class IovationCheckRequest(Model):
    is_demo = BooleanType(default=False)
    credentials = ModelType(IovationCredentials, default=None)
    input_data = ModelType(CheckInput, required=True)

    def validate_credentials(self, data, value):
        if not self.is_demo and value is None:
            raise ValidationError('This field is required')


class IovationIpLocation(Model):
    city = StringType()
    country_code = StringType(serialized_name="countryCode")
    region = StringType()


class IpDetails(Model):
    address = StringType()
    ip_location = ModelType(IovationIpLocation, serialized_name="ipLocation")


class DeviceEntity(Model):
    type = StringType()
    alias = IntType()


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
    score = IntType()
    rules_matched = IntType(serialized_name="rulesMatched")
    rules = ListType(ModelType(IovationDeviceFraudRule))


class DeviceCheckDetails(Model):
    device = ModelType(DeviceEntity)
    real_ip = ModelType(IpDetails, serialized_name="realIp")
    rule_results = ModelType(DeviceFraudRuleResults, serialized_name="ruleResults")


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


class IPLocation(Model):
    ip_address = StringType()
    country = StringType()
    region = StringType()
    city = StringType()


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
    ip_location = ModelType(IPLocation)

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

        if output.details.rule_results:
            matched_rules = []
            for rule in output.details.rule_results.rules:
                matched_rules.append(rule.as_passfort_device_fraud_rule())
            device_fraud_detection.matched_rules = matched_rules


        ip_location = IPLocation()
        if output.details and output.details.real_ip:
            ip_location.ip_address = output.details.real_ip.address
            ip_location.country = pycountry.countries.get(alpha_2=output.details.real_ip.ip_location.country_code).alpha_3
            ip_location.region = output.details.real_ip.ip_location.region
            ip_location.city = output.details.real_ip.ip_location.city

        return cls({
            'device_metadata': device_metadata,
            'device_fraud_detection': device_fraud_detection,
            'ip_location': ip_location
        })
