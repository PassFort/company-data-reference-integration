from enum import unique
from schematics import Model
from schematics.types import BooleanType, StringType, ModelType, DateType, ListType, DictType
from .errors import VSureServiceException


class VisaCheckResponseOutput(Model):
    id = StringType()
    time_of_check = StringType(deserialize_from='Time of Check')
    result = StringType(choices=['OK', 'Error'])
    status = StringType()
    visa_details = DictType(StringType, deserialize_from='Visa Details')
    work_entitlement = StringType(deserialize_from='Work Entitlement')
    visa_conditions = StringType(deserialize_from='Visa Conditions')
    conditions = StringType()


class VSureVisaCheckResponse(Model):
    error = StringType()
    output = ModelType(VisaCheckResponseOutput)

    @classmethod
    def from_raw(cls, response):
        try:
            raw_response = response.json()
            return raw_response, cls.from_json(raw_response)
        except JSONDecodeError:
            return {}, None

    @classmethod
    def from_json(cls, data):
        model = cls().import_data(data, apply_defaults=True)
        model.validate()
        return model


class Visa(Model):
    country_code = 'AUS'
    grant_date = StringType(required=True)
    expiry_date = StringType(required=True)
    name = StringType(required=True)
    entitlement = StringType(choices=['WORK', 'STUDY'], required=True)
    source = 'VEVO'
    details = DictType(StringType)


class VisaCheck(Model):
    visas = ListType(ModelType(Visa))
    failure_reason = StringType()

    @staticmethod
    def from_raw_data(raw_data: VSureVisaCheckResponse, visa_check_type):
        if raw_data.output.result == 'Error':
            raise VSureServiceException(raw_data.output.status)

        visa = Visa()

        visa.grant_date = raw_data.output.visa_details['Grant Date']
        visa.expiry_date = raw_data.output.visa_details['Expiry Date']
        visa.name = raw_data.output.visa_details['Visa Type Name']
        visa.entitlement = visa_check_type
        visa.details = {
            "Work Entitlement Description": raw_data.output.work_entitlement,
            "Visa Applicant": raw_data.output.visa_details['Visa Applicant'],
            "Visa Class": raw_data.output.visa_details['Visa Class'],
            "Visa Type": raw_data.output.visa_details['Visa Type'],
            "Visa Type Details": raw_data.output.visa_details['Visa Type Details'],
            "Visa Conditions": raw_data.output.visa_conditions,
            "Conditions": raw_data.output.conditions
        }

        visa.validate()

        return VisaCheck({
            'visas': [visa],
            'failure_reason': raw_data.error
        })
