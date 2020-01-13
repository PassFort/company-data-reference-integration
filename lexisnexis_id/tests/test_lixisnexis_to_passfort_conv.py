import pytest 
from lexisnexis.convert_data import lexisnexis_to_passfort_data

def test_empty_package(client):
    response_body = lexisnexis_to_passfort_data({'status': 200, 'body':{}})

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL"
                                },
                                "raw": {},
                                "errors": []
                            }

def test_record_with_empty_datasource_results(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {}
                }
            }
        }
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }    


def test_record_with_one_datasource_with_surname_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "Name": {
                                "Last": "BECKMAN"
                            }
                        },
                        "VerifiedInput": {
                            "Name": {
                                "Last": "BECKMAN"
                            }
                        }
                    }
                }
            }
        }
    }
    
    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['SURNAME']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  

def test_record_with_one_datasource_with_forename_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "Name": {
                                "First": "MATHEW"
                            }
                        },
                        "VerifiedInput": {
                            "Name": {
                                "First": "MATHEW"
                            }
                        }
                    }
                }
            }
        }
    }
    
    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['FORENAME']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  


def test_record_with_one_datasource_with_dob_complete_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "DOB": {
                                    "Year": 1980,
                                    "Month": 4,
                                    "Day": 6
                            }
                        },
                        "VerifiedInput": {
                            "DOB": {
                                "Year": 1980,
                                "Month": 4,
                                "Day": 6
                            }
                        }
                    }
                }
            }
        }
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  

def test_record_with_one_datasource_with_dob_year_month_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "DOB": {
                                    "Year": 1980,
                                    "Month": 4
                            }
                        },
                        "VerifiedInput": {
                            "DOB": {
                                "Year": 1980,
                                "Month": 4
                            }
                        }
                    }
                }
            }
        }
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  

def test_record_with_one_datasource_with_dob_year_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "DOB": {
                                    "Year": 1980
                            }
                        },
                        "VerifiedInput": {
                            "DOB": {
                                "Year": 1980
                            }
                        }
                    }
                }
            }
        }
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  


def test_record_with_one_datasource_with_dob_day_nomatch(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "DOB": {
                                    "Year": 1980
                            }
                        }
                    }
                }
            }
        }
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  

def test_record_with_one_datasource_with_address_match(client):
    lexisnexis_data = {'status': 200, 'body':
        {
            "InstantIDResponseEx": {
                "response": {
                    "Result": {
                        "InputEcho": {
                            "Address": {
                                "Zip5": "41063",
                            }
                        },
                        "VerifiedInput": {
                            "Address": {
                                "StreetAddress1": "LUNSFORD",
                                "City": "MORNING VIEW",
                                "State": "KY",
                                "Zip5": "41063",
                                "Zip4": "4106",
                                "County": "CHEROKEE"
                            }
                        }
                    }
                }
            }
        }
    }
    
    response_body = lexisnexis_to_passfort_data(lexisnexis_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'LexisNexis DB',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['ADDRESS']
                                            }
                                        ]
                                    },
                                    "decision": "PASS"
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": []
                            }  


def test_record_error_bad_request(client):
    lexisnexis_data = {'status': 500, 'body':
        'Bad request message'
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": [{'code': 303, 'message': f'Provider Error: UNKNOW ERROR: {lexisnexis_data["body"]}'}]
                            } 

def test_record_error_auth_error(client):
    lexisnexis_data = {'status': 401, 'body':
        'Auth Error'
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": [{'code': 302, 'message': 'Provider Error: IP address that is not on the white list or invalid credentials'}]
    }

def test_record_error_service_timeout(client):
    lexisnexis_data = {'status': 408, 'body':
        'Timeout'
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": [{'code': 403, 'message': 'Provider Error: TIMEOUT'}]
    }

def test_record_error_server_error(client):
    lexisnexis_data = {'status': 500, 'body':
        'TimeoutInternal Server Error'
    }

    response_body = lexisnexis_to_passfort_data(lexisnexis_data)
    assert response_body == {
                                "output_data": {
                                    'decision': 'ERROR'
                                },
                                "raw": lexisnexis_data['body'],
                                "errors": [{'code': 303, 'message': f"Provider Error: UNKNOW ERROR: {lexisnexis_data['body']}"}]
    }