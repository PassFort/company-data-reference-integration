import pytest

from api.demo_response import create_demo_response


def test_fail_package(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Fail']
                }
            }
        }
    }
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [],
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": [],
    }

    response = create_demo_response(input_data)
    assert response == demo_response


def test_full_valid_package(client):
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "DOB",
        "IDENTITY_NUMBER",
    ]
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd']
                }
            }
        }
    }
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'LexisNexis DB',
                        "database_type": 'CIVIL',
                        "matched_fields": matched_fields,
                        "count": 1
                    }
                ]
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    response = create_demo_response(input_data)
    assert response == demo_response


def test_partial_valid_package(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Partial']
                }
            }
        },
        'config': {
            'use_dob': False,
            'require_identity_number': False,
        }
    }
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "DOB"
    ]
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'LexisNexis DB',
                        "database_type": 'CIVIL',
                        "matched_fields": matched_fields,
                        "count": 1
                    }
                ]
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    response = create_demo_response(input_data)
    assert response == demo_response


def test_partial_with_required_dob(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Partial']
                }
            }
        },
        'config': {
            'use_dob': True,
            'require_identity_number': False,
        }
    }
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "IDENTITY_NUMBER"
    ]
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'LexisNexis DB',
                        "database_type": 'CIVIL',
                        "matched_fields": matched_fields,
                        "count": 1
                    }
                ]
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    response = create_demo_response(input_data)
    assert response == demo_response

def test_partial_with_required_ssn(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Partial']
                }
            }
        },
        'config': {
            'use_dob': False,
            'require_identity_number': True,
        }
    }
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "DOB"
    ]
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'LexisNexis DB',
                        "database_type": 'CIVIL',
                        "matched_fields": matched_fields,
                        "count": 1
                    }
                ]
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    response = create_demo_response(input_data)
    assert response == demo_response
