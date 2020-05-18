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
                    "detailList": ""
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
                                        "matches": []
                                    }
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
                                                "database_name": "Commercial",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ],
                                                "count": 3
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
                                                "database_name": "Commercial",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ],
                                                "count": 3
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
                                                "database_name": "Commercial",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS"
                                                ],
                                                "count": 4
                                            }
                                        ]
                                    }
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
                                                "database_name": "Commercial",
                                                "database_type": "CIVIL",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS"
                                                ],
                                                "count": 4
                                            },
                                            {
                                                "database_name": "Credit",
                                                "database_type": "CREDIT",
                                                "matched_fields": [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB",
                                                    "ADDRESS"
                                                ],
                                                "count": 4
                                            }
                                        ]
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
                                "errors": [{'code': 303, 'message': f'Provider Error: UNKNOW ERROR: {worldview_data["body"]}'}]
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
                                "errors": [{'code': 303, 'message': 'Provider Error: UNKNOW ERROR: Not found!'}]
    }