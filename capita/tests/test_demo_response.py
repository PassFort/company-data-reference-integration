import pytest 

from api.demo_response import create_demo_response

matched_fields = [
    "FORENAME",
    "SURNAME",
    "ADDRESS",
    "DOB"
]

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
        "output_data": {},
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
    demo_response = {
        "output_data": {
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
    demo_response = {
        "output_data": {
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

def test_mortality_fail(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'MORTALITY']
                }
            }
        }
    }
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "decision": "FAIL",
            "electronic_id_check": {
                "matches": [
                {
                    "database_name": 'Death register',
                    "database_type": 'MORTALITY',
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

def test_mortality_1_plus_1_fail(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'MORTALITY1+1']
                }
            }
        }
    }
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "decision": "FAIL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'Death register',
                        "database_type": 'MORTALITY',
                        "matched_fields": matched_fields,
                        "count": 1
                    },
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


def test_mortality_2_plus_2_fail(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'MORTALITY2+2']
                }
            }
        }
    }
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "decision": "FAIL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'Death register',
                        "database_type": 'MORTALITY',
                        "matched_fields": matched_fields,
                        "count": 1
                    },
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
