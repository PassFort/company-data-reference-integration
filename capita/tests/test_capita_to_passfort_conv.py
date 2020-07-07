import pytest 
from capita.convert_data import capita_to_passfort_data

def test_empty_package(client):
    response_body = capita_to_passfort_data({'status': 200, 'body':{}})

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": {},
                                "errors": []
                            }

def test_record_with_empty_datasource_results(client):
    capita_data = {'status': 200, 'body':
        {
            "About": {
                "TransactionReference": "EmptyResults",
            },
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Electoral Role (Proof of DOB)",
                                "Result": 0,
                                "Error": "Matching Address Not Found",
                            },
                            {
                                "CheckName": "Credit Bureau (Proof of DOB)",
                                "Result": 0,
                                "Error": "Matching Address Not Found",
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL",
                                    'electronic_id_check': {
                                        'provider_reference_number': 'EmptyResults',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': []},
                                            {
                                                'database_name': 'Credit Bureau',
                                                'database_type': 'CREDIT',
                                                'matched_fields': []
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": [
                                    {
                                        'code': 303,
                                        'message': 'Provider Error: UNKNOWN ERROR: Matching Address Not Found'
                                    }
                                ]
                            }    




def test_record_with_one_datasource_with_dob_forename_surname_match(client):
    capita_data = {'status': 200, 'body':
        {
            "About": {
                "TransactionReference": "SurnameMatch",
            },
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Electoral Role (Proof of DOB)",
                                "Result": 1,
                                "Error": None,
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    'electronic_id_check': {
                                        'provider_reference_number': 'SurnameMatch',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ]
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            }


def test_record_with_one_datasource_with_address_forename_surname_match(client):
    capita_data = {'status': 200, 'body':
        {
            "About": {
                "TransactionReference": "ForenameMatch",
            },
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Electoral Role (Proof of Address)",
                                "Result": 1,
                                "Error": None,
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }
    
    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    'electronic_id_check': {
                                        'provider_reference_number': 'ForenameMatch',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ]
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            } 

def test_record_with_one_datasource_with_full_match(client):
    capita_data = {'status': 200, 'body':
        {
            "About": {
                "TransactionReference": "FullMatch",
            },
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Electoral Role (Proof of Address)",
                                "Result": 1,
                                "Error": None,
                            },
                            {
                                "CheckName": "Electoral Role (Proof of DOB)",
                                "Result": 1,
                                "Error": None,
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }
    
    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    'electronic_id_check': {
                                        'provider_reference_number': 'FullMatch',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS",
                                                    "DOB"
                                                ]
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            } 

def test_record_with_one_datasource_with_full_match_diff_database(client):
    capita_data = {'status': 200, 'body':
        {
            "About": {
                "TransactionReference": "FullMatchDiff",
            },
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Electoral Role (Proof of Address)",
                                "Result": 1,
                                "Error": None,
                            },
                            {
                                "CheckName": "Credit Bureau (Proof of DOB)",
                                "Result": 1,
                                "Error": None,
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }
    
    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    'electronic_id_check': {
                                        'provider_reference_number': 'FullMatchDiff',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ]
                                            },
                                            {
                                                'database_name': 'Credit Bureau',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ]
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            } 

def test_record_with_one_datasource_with_mortality_match(client):
    capita_data = {'status': 200, 'body':
        {
            "Response": {
                "Result": [
                    {
                        "Name": "Stage1",
                        "CheckResults": [
                            {
                                "CheckName": "Death register",
                                "Result": 1,
                                "Error": None,
                            },
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL",
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Death register',
                                                'database_type': 'MORTALITY',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ]
                                            },
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            }

def test_record_error_bad_request(client):
    capita_data = {'status': 500, 'body':
        'Bad request message'
    }

    response_body = capita_to_passfort_data(capita_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": capita_data['body'],
                                "errors": [{'code': 303, 'message': f'Provider Error: UNKNOWN ERROR: {capita_data["body"]}'}]
                            }

def test_record_error_auth_error(client):
    capita_data = {'status': 200, 'body':
        {
            "Response": {
                "Result": [],
                "Error": "10100302"
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": capita_data['body'],
                                "errors": [{'code': 302, 'message': f'Provider Error: Required credentials are missing for the request.'}]
    }


def test_record_error_required_fields(client):
    capita_data = {'status': 200, 'body':
        {
            "Response": {
                "Result": [],
                "Error": "10100401"
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": capita_data['body'],
                                "errors": [{'code': 101, 'message': f'Provider Error: Please validate Applicant Detail, mandatory field missing.'}]
    }

def test_record_generic_error_provider(client):
    capita_data = {'status': 200, 'body':
        {
            "Response": {
                "Result": [],
                "Error": "10101000"
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": capita_data['body'],
                                "errors": [{'code': 303, 'message': f'Provider Error: Error in Executing Request.'}]
    }
