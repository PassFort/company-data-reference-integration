from app.api.errors import VSureServiceException
from app.api.input_types import IndividualData
from app.api.output_types import VSureVisaCheckResponse, VisaCheck
from app.application import app
import json
import responses
from schematics.exceptions import DataError
import unittest


class TestInputData(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    def test_invalid_input(self):
        response = self.testing_app.post('/visa-check', content_type='application/json', json={
            'config': {'visa_check_type': 'WORK'},
            'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
            'input_data': {
                'documents_metadata': [{
                    'document_type': 'PASSPORT',
                    'number': '123134235',
                    'country_code': 'IND'
                }],
                'personal_details': {
                    'dob': 'invalid date',
                    'name': {
                        'family_name': 'Smith',
                        'given_names': ['John']
                    }
                }
            },
            'is_demo': False
        })

        self.assertEqual(400, response.status_code)

    def test_date_format(self):
        individual_data = IndividualData({
            'personal_details': {
                'name': {
                    'given_names': ['John', 'Tom'],
                    'family_name': 'Smith'
                },
                'dob': 'blah'
            },
            'documents_metadata': [{
                'document_type': 'PASSPORT',
                'number': '12378298547',
                'country_code': 'FRA'
            }]
        })

        with self.assertRaises(DataError):
            individual_data.validate()

    def test_as_visa_holder_data(self):

        individual_data = IndividualData({
            'personal_details': {
                'name': {
                    'given_names': ['John', 'Tom'],
                    'family_name': 'Smith'
                },
                'dob': '1999-01-04'
            },
            'documents_metadata': [{
                'document_type': 'PASSPORT',
                'number': '12378298547',
                'country_code': 'FRA'
            }]
        })

        visa_holder = individual_data.as_visa_holder_data()

        self.assertEqual('John Tom', visa_holder.given_names)
        self.assertEqual('Smith', visa_holder.family_name)
        self.assertEqual('1999-01-04', visa_holder.date_of_birth)
        self.assertEqual('12378298547', visa_holder.passport_id)
        self.assertEqual('FRA', visa_holder.country)


class TestOutputData(unittest.TestCase):

    def test_successful_output(self):
        test_response = {
            "output": {
                "id": "4324234",
                "Time of Check": "Tuesday February 23, 2016, 16:48:36 (EST) Canberra, Australia (GMT +1100)",
                "Person Checked": {
                    "Name": "John Smith",
                    "DOB": "06 Jul 1993",
                    "Passport ID": "12345678989",
                    "Nationality": "FRA"
                },
                "status": "",
                "result": "OK",
                "Visa Details": {
                    "Visa Applicant": "Primary",
                    "Visa Class": "12",
                    "Visa Type": 573,
                    "Visa Type Name": "Higher Education Sector",
                    "Grant Date": "07 Jun 2009",
                    "Expiry Date": "07 Jun 2019",
                    "Visa Type Details": "Visa type details"
                },
                "Study Condition": "No limitations on study.",
                "Visa Conditions": "8202,8533",
                "conditions": "here are some conditions",
                "haspdf": 1,
                "token": "XXXXXXXXXXXXXXX"
            },
            "error": ""
        }

        raw_response, response_model = VSureVisaCheckResponse.from_json(test_response)

        visa_check = VisaCheck.from_visa_check_response(response_model, "STUDY")

        expected_output = {
            "visas": [{
                'holder': {
                    "full_name": "John Smith",
                    "dob": "1993-07-06",
                    'document_checked': {
                        'document_type': 'PASSPORT',
                        'number': '12345678989',
                        'country_code': 'FRA'
                    }
                },
                "country_code": "AUS",
                "grant_date": "2009-06-07",
                "expiry_date": "2019-06-07",
                "name": "Higher Education Sector",
                "entitlement": "STUDY",
                "details": [
                    {"name": "Study Condition", "value": "No limitations on study."},
                    {"name": "Visa Applicant", "value": "Primary"},
                    {"name": "Visa Class", "value": "12"},
                    {"name": "Visa Type", "value": "573"},
                    {"name": "Visa Type Details", "value": "Visa type details"},
                    {"name": "Visa Conditions", "value": "8202,8533"},
                    {"name": "Conditions", "value": "here are some conditions"}
                ]
            }],
            "failure_reason": ""
        }

        self.assertEqual(expected_output, visa_check.to_primitive())


    def test_failed_output(self):
        failed_response = {
            "output": {
                "id": "12345",
                "Time of Check": "Tuesday February 23, 2016, 16:48:36 (EST) Canberra, Australia (GMT +1100)",
                "Person Checked": {
                    "Name": "John Smith",
                    "DOB": "12 Mar 2000",
                    "Passport ID": "1212121212",
                    "Nationality": "FIN"
                },
                "status": "",
                "result": "OK",
                "Visa Details": {
                    "Visa Type": 0,
                    "Grant Date": "N/A",
                    "Expiry Date": "N/A",
                    "Visa Type Details": ""
                },
                "Work Entitlement": "",
                "Visa Conditions": "",
                "conditions": "",
                "haspdf": 0,
                "token": "XXXXXXXXXXXXXXX"
            },
            "error": "Error: Does not hold a valid visa"
        }

        raw_response, response_model = VSureVisaCheckResponse.from_json(failed_response)

        visa_check = VisaCheck.from_visa_check_response(response_model, "WORK")

        expected_output = {
            "visas": [{
                'holder': {
                    "full_name": "John Smith",
                    "dob": "2000-03-12",
                    'document_checked': {
                        'document_type': 'PASSPORT',
                        'number': '1212121212',
                        'country_code': 'FIN',
                    }
                },
                "country_code": 'AUS',
                "grant_date": None,
                "expiry_date": None,
                "name": "WORK",
                "entitlement": "WORK",
                "details": [
                    {"name": "Visa Type", "value": "0"}
                ]
            }],
            "failure_reason": "Error: Does not hold a valid visa"
        }

        self.assertEqual(expected_output, visa_check.to_primitive())


    def test_error_output(self):
        error_response = {
            'output': '',
            'error': 'Here is an error'
        }

        with self.assertRaises(VSureServiceException):
            raw_response, response_model = VSureVisaCheckResponse.from_json(error_response)
