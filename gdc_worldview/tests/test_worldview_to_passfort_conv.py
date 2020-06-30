import pytest 
from worldview.convert_data import worldview_to_passfort_data

def test_empty_package(client):
    response_body = worldview_to_passfort_data({'status': 200, 'body':{}})

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
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "30",
                    "messages": [],
                    "detailList": "",
                    "detailCode": "WS-3908188.2020.4.26.test",
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [],
                                        "provider_reference_number": "WS-3908188.2020.4.26.test"
                                    },
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }


def test_record_with_one_datasource_with_dob_forename_surname_match(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        }
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_one_datasource_with_identity_number_match(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-NATIONALID",
                            "value": "Full match was made on National ID"
                        }
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_one_datasource_with_address_forename_surname_match(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM1-HOUSENUMBER",
                            "value": "Full match was made on House Number/Street Number"
                        },
                        {
                            "code": "1MT-FR-CMM1-THOROUGHFARE",
                            "value": "Full match was made on Street/Thoroughfare"
                        },
                        {
                            "code": "1MT-FR-CMM1-LOCALITY",
                            "value": "Full match was made on City/Locality"
                        },
                        {
                            "code": "4MT-FR-CMM1-SUBPREMISE",
                            "value": "Datasource does not contain element Sub Premise Descriptors provided in Address Lines"
                        }   
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_one_datasource_with_full_match(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CMM1-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM1-HOUSENUMBER",
                            "value": "Full match was made on House Number/Street Number"
                        },
                        {
                            "code": "1MT-FR-CMM1-THOROUGHFARE",
                            "value": "Full match was made on Street/Thoroughfare"
                        },
                        {
                            "code": "1MT-FR-CMM1-LOCALITY",
                            "value": "Full match was made on City/Locality"
                        },
                        {
                            "code": "4MT-FR-CMM1-SUBPREMISE",
                            "value": "Datasource does not contain element Sub Premise Descriptors provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM1-NATIONALID",
                            "value": "Full match was made on National ID"
                        }
                    ],
                    "detailList": "",
                    "detailCode": "WS-3908188.2020.4.26.test",
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            }
                                        ],
                                        "provider_reference_number": "WS-3908188.2020.4.26.test"
                                    },
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }


def test_record_with_one_datasource_with_full_match_diff_database(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CMM1-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM1-NATIONALID",
                            "value": "Full match was made on National ID"
                        },  
                        {
                            "code": "1MT-FR-CRD14-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CRD14-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CRD14-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CRD14-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CRD14-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CRD14-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CRD14-NATIONALID",
                            "value": "Full match was made on National ID"
                        } 
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            },
                                            {
                                                "database_name": "Credit (source #14)",
                                                "database_type": "CREDIT",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_one_datasource_with_full_match_diff_database_in_the_same_code(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "10",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CMM1-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM1-NATIONALID",
                            "value": "Full match was made on National ID"
                        }, 
                        {
                            "code": "1MT-FR-CMM2-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM2-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM2-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM2-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM2-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CMM2-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CMM2-NATIONALID",
                            "value": "Full match was made on National ID"
                        },
                        {
                            "code": "1MT-FR-CRD4-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CRD4-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CRD4-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CRD4-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CRD4-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        },
                        {
                            "code": "1MT-FR-CRD4-ADDRESS",
                            "value": "Full match was made on address elements provided in Address Lines"
                        },
                        {
                            "code": "1MT-FR-CRD4-NATIONALID",
                            "value": "Full match was made on National ID"
                        } 
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            },
                                            {
                                                "database_name": "Commercial (source #2)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            },
                                            {
                                                "database_name": "Credit (source #4)",
                                                "database_type": "CREDIT",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS",
                                                    "IDENTITY_NUMBER"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_reliability_20_match(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "20",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        }
                    ],
                    "detailList": ""
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "PASS",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [
                                            {
                                                "database_name": "Commercial (source #1)",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ],
                                                "count": 1
                                            }
                                        ]
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }    

def test_record_with_reliability_30_nomatch(client):
    worldview_data = {'status': 200, 'body':
        {   
            "identity": {
                "codes": {
                    "reliability": "30",
                    "messages": [
                        {
                            "code": "1MT-FR-CMM1-COMPLETENAME",
                            "value": "Full match was made on Complete Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTINITIAL",
                            "value": "Full match was made on First Initial"
                        },
                        {
                            "code": "1MT-FR-CMM1-FIRSTNAME",
                            "value": "Full match was made on First Name/Given Name"
                        },
                        {
                            "code": "1MT-FR-CMM1-LASTNAME",
                            "value": "Full match was made on Last Name/Surname "
                        },
                        {
                            "code": "1MT-FR-CMM1-DATEOFBIRTH",
                            "value": "Full match was made on Date of Birth"
                        }
                    ],
                    "detailList": "",
                    "detailCode": "WS-3908188.2020.4.26.test",
                }
            }
        }
    }

    response_body = worldview_to_passfort_data(worldview_data)

    assert response_body == {
                                "output_data": {
                                    "decision": "FAIL",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {
                                        "matches": [],
                                        "provider_reference_number": "WS-3908188.2020.4.26.test"
                                    }
                                },
                                "raw": worldview_data['body'],
                                "errors": []
                            }        

def test_record_error_bad_request(client):
    worldview_data = {'status': 500, 'body':
        'Bad request message'
    }

    response_body = worldview_to_passfort_data(worldview_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": worldview_data['body'],
                                "errors": [{'code': 303, 'message': f'Provider Error: UNKNOWN ERROR: {worldview_data["body"]}'}]
                            }

def test_record_error_auth_error(client):
    worldview_data = {'status': 401, 'body': 'Auth failure'}

    response_body = worldview_to_passfort_data(worldview_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": worldview_data['body'],
                                "errors": [{'code': 302, 'message': 'Provider Error: Required credentials are missing for the request.'}]
    }


def test_record_generic_error_provider(client):
    worldview_data = {'status': 404, 'body': 'Not found!'}

    response_body = worldview_to_passfort_data(worldview_data)
    assert response_body == {
                                "output_data": {
                                    "decision": "ERROR",
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": worldview_data['body'],
                                "errors": [{'code': 303, 'message': 'Provider Error: UNKNOWN ERROR: Not found!'}]
    }