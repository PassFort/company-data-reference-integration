import re
import logging
from functools import partial
from typing import List

from onfido.models import Applicant, Check, IdentityReport


def stage_error_from_onfido_response(response, connection_error_message):
    if isinstance(response, dict):
        errors = response.get('error')
        return {
            "error": errors,
        }
    else:
        return {
            "error": connection_error_message,
        }


def onfido_check_to_individual(applicant_json, check_json, use_dob):
    applicant = Applicant().import_data(applicant_json, apply_defaults=True)
    check = Check().import_data(check_json, apply_defaults=True)

    has_ssn = len(applicant.id_numbers) > 0

    matches = []
    for report in check.reports:
        if isinstance(report, IdentityReport):
            matches = report.compute_matches(applicant.country.upper(), has_ssn)
            break

    if use_dob:
        config = {
            'rules': [
                {
                    'name': 'Found on mortality list',
                    'result': 'Fail',
                    'database_types': ['MORTALITY'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'DOB'],
                            'count': 1,
                        }
                    ]
                },
                {
                    'name': 'Matches name and address plus name and DOB',
                    'result': '2+2',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'distinct_sources': False,
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS'],
                            'count': 1,
                        },
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'DOB'],
                            'count': 1,
                        },
                    ]
                },
                {
                    'name': 'Matches name and address from two sources',
                    'result': '2+2',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS', 'DOB'],
                            'count': 2,
                        },
                    ]
                },
                {
                    'name': 'Matches name and address',
                    'result': '1+1',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS', 'DOB'],
                            'count': 1,
                        },
                    ]
                },
            ]
        }
    else:
        config = {
            'rules': [
                {
                    'name': 'Found on mortality list',
                    'result': 'Fail',
                    'database_types': ['MORTALITY'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'DOB'],
                            'count': 1,
                        }
                    ]
                },
                {
                    'name': 'Matches name and address plus name and DOB',
                    'result': '2+2',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'distinct_sources': False,
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS'],
                            'count': 1,
                        },
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'DOB'],
                            'count': 1,
                        },
                    ]
                },
                {
                    'name': 'Matches name and address from two sources',
                    'result': '2+2',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS'],
                            'count': 2,
                        },
                    ]
                },
                {
                    'name': 'Matches name and address',
                    'result': '1+1',
                    'database_types': ['CREDIT', 'CIVIL'],
                    'requires': [
                        {
                            'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS'],
                            'count': 1,
                        },
                    ]
                },
            ]
        }

    return {
        'matches': matches,
        'config': config,
    }
