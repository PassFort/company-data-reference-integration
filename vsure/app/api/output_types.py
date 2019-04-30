from datetime import datetime
from enum import unique
import json
from schematics import Model
from schematics.exceptions import DataError, ValidationError
from schematics.types import BooleanType, StringType, ModelType, DateType, ListType, DictType
from .errors import VSureServiceException
from .input_types import DocumentMetadata


def format_date(value):
    try:
        if not value or value == 'N/A':
            return None
        date = datetime.strptime(value, '%d %b %Y')
        return date.strftime('%Y-%m-%d')
    except (ValueError, TypeError):
        raise ValidationError(f'Input is not valid date: {value}')


class PersonChecked(Model):
    name = StringType(deserialize_from='Name', required=True)
    dob = StringType(deserialize_from='DOB', required=True)
    passport_id = StringType(deserialize_from='Passport ID', required=True)
    nationality = StringType(deserialize_from='Nationality', required=True)


class NameValueType(Model):
    name = StringType(required=True)
    value = StringType(required=True)


class VisaCheckResponseOutput(Model):
    id = StringType()
    time_of_check = StringType(deserialize_from='Time of Check')
    result = StringType(choices=['OK', 'Error'])
    status = StringType()
    person_checked = ModelType(PersonChecked, deserialize_from='Person Checked')
    visa_details = DictType(StringType, deserialize_from='Visa Details', default=None)
    work_entitlement = StringType(deserialize_from='Work Entitlement', default=None)
    study_condition = StringType(deserialize_from='Study Condition', default=None)
    visa_conditions = StringType(deserialize_from='Visa Conditions')
    conditions = StringType()


class VSureVisaCheckResponse(Model):
    error = StringType()
    output = ModelType(VisaCheckResponseOutput)

    @classmethod
    def from_json(cls, response):
        if response.get('error') and not response.get('output'):
            raise VSureServiceException(response['error'], response)

        model = cls().import_data(response, apply_defaults=True)
        model.validate()

        return response, model



class VisaHolder(Model):
    full_name = StringType()
    dob = StringType()
    document_checked = ModelType(DocumentMetadata)


class Visa(Model):
    holder = ModelType(VisaHolder)
    country_code = StringType(choices=['AUS'], required=True, default='AUS')
    grant_date = StringType()
    expiry_date = StringType()
    name = StringType()
    entitlement = StringType(choices=['WORK', 'STUDY'], required=True)
    source = 'VEVO'
    details = ListType(ModelType(NameValueType))

    def add_details(self, output):
        self.details = []

        self.add_detail("Work Entitlement Description", output.work_entitlement)
        self.add_detail("Study Condition", output.study_condition)

        if 'Visa Applicant' in output.visa_details.keys():
            self.add_detail("Visa Applicant", output.visa_details['Visa Applicant'])
        if 'Visa Class' in output.visa_details.keys():
            self.add_detail("Visa Class", output.visa_details['Visa Class'])
        if 'Visa Type' in output.visa_details.keys():
            self.add_detail("Visa Type", output.visa_details['Visa Type'])
        if 'Visa Type Details' in output.visa_details.keys():
            self.add_detail("Visa Type Details", output.visa_details['Visa Type Details'])

        self.add_detail("Visa Conditions", output.visa_conditions)
        self.add_detail("Conditions", output.conditions)


    def add_detail(self, name, value):
        if value:
            self.details.append({'name': name, 'value': value})


class VisaCheck(Model):
    visas = ListType(ModelType(Visa))
    failure_reason = StringType()

    @staticmethod
    def from_visa_check_response(raw_data: VSureVisaCheckResponse, visa_check_type):
        if raw_data.output.result == 'Error':
            # We want this error to be a "failure" instead of an error, we check on this string as vSure don't send error codes
            if raw_data.output.status == 'Could not complete visa check - The Department has not been able to identify the person. Please check that the details you entered in are correct.':
                visa_check = VisaCheck({
                    'visas': [],
                    'failure_reason': raw_data.output.status
                })
                visa_check.validate()
                return visa_check
            else:
                raise VSureServiceException(raw_data.output.status, json.dumps(raw_data.to_primitive()))

        visa = Visa()

        if raw_data.output.visa_details:
            visa.grant_date = format_date(raw_data.output.visa_details.get('Grant Date'))
            visa.expiry_date = format_date(raw_data.output.visa_details.get('Expiry Date'))
            visa.name = raw_data.output.visa_details.get('Visa Type Name') or visa_check_type
            visa.add_details(raw_data.output)

        visa.holder = {
            'full_name': raw_data.output.person_checked.name,
            'dob': format_date(raw_data.output.person_checked.dob),
            'document_checked': {
                'document_type': 'PASSPORT',
                'number': raw_data.output.person_checked.passport_id,
                'country_code': raw_data.output.person_checked.nationality
            }
        }

        visa.entitlement = visa_check_type

        visa.validate()

        visa_check = VisaCheck({
            'visas': [visa],
            'failure_reason': raw_data.error
        })

        visa_check.validate()

        return visa_check
