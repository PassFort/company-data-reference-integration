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
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    response = create_demo_response(input_data)
    assert response == demo_response

def test_full_valid_package(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd']
                }
            }
        }
    }
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "ADDRESS",
        "DOB"
    ]
    demo_response = {
        "output_data": {
            'decision': 'PASS',
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'Credit Agency',
                        "database_type": 'CREDIT',
                        "matched_fields": matched_fields,
                        "count": 1
                    },
                    {
                        "database_name": 'Electoral Roll',
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

def test_1_plus_1_valid_package(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', '1+1']
                }
            }
        }
    }
    matched_fields = [
        "FORENAME",
        "SURNAME",
        "ADDRESS",
        "DOB"
    ]
    demo_response = {
        "output_data": {
            'decision': 'PASS',
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'Credit Agency',
                        "database_type": 'CREDIT',
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