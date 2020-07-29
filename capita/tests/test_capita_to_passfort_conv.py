import pytest 
from capita.convert_data import capita_to_passfort_data

def test_empty_package(client):
    response_body = capita_to_passfort_data({'status': 200, 'body':{}})

    assert response_body == {
                                "output_data": {
                                    "entity_type": "INDIVIDUAL",
                                    "electronic_id_check": {"matches": []}
                                },
                                "raw": {},
                                "errors": []
                            }

def test_record_with_empty_datasource_results(client):
    capita_data = {'status': 200, 'body':
        {
            "Key": "EmptyResults",
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
                                    'electronic_id_check': {
                                        'provider_reference_number': 'EmptyResults',
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [],
                                                'count': 0
                                            },
                                            {
                                                'database_name': 'Credit Bureau',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [],
                                                'count': 0
                                            }
                                        ]
                                    },
                                    'entity_type': 'INDIVIDUAL'
                                },
                                "raw": capita_data['body'],
                                "errors": []
                            }    


def test_record_with_one_datasource_with_dob_forename_surname_match(client):
    capita_data = {'status': 200, 'body':
        {
            "Key": "SurnameMatch",
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
                                                ],
                                                'count': 1
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
            "Key": "ForenameMatch",
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
                                                ],
                                                'count': 1
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
            "Key": "FullMatch",
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
                                                ],
                                                'count': 1
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
            "Key": "FullMatchDiff",
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
                    },
                    {
                        "Name": "Stage2",
                        "Conditions": [
                            {
                                "If": 1,
                                "Then": 0,
                                "NextStageIndex": 3
                            },
                            {
                                "If": 2,
                                "Then": 1,
                                "NextStageIndex": 3
                            }
                        ],
                        "StageResult": 1,
                        "CheckResults": [
                            {
                                "Rules": [
                                    {
                                        "CheckFilters": [
                                            {
                                                "RuleId": 2297,
                                                "CheckFilterId": 10,
                                                "FilterShortCode": "HaloLevel10",
                                                "FilterParameter": {
                                                    "Key": None,
                                                    "Value": "1"
                                                }
                                            }
                                        ],
                                        "FilterShortCode": "HaloLevel10",
                                        "FilterParameter": "1",
                                        "Comparator": 0,
                                        "CheckAmount": 0,
                                        "RuleResult": 2,
                                        "PotName": "Fail",
                                        "AlertMessage": None,
                                        "LastUpdatedDate": "2016-11-22T16:27:08Z"
                                    },
                                    {
                                        "CheckFilters": [
                                            {
                                                "RuleId": 2300,
                                                "CheckFilterId": 10,
                                                "FilterShortCode": "HaloLevel10",
                                                "FilterParameter": {
                                                    "Key": None,
                                                    "Value": "1"
                                                }
                                            }
                                        ],
                                        "FilterShortCode": "HaloLevel10",
                                        "FilterParameter": "1",
                                        "Comparator": 2,
                                        "CheckAmount": 0,
                                        "RuleResult": 1,
                                        "PotName": "Not Matched",
                                        "LastUpdatedDate": "2016-11-22T16:27:08Z"
                                    }
                                ],
                                "StageName": "Stage2",
                                "CheckName": "Death Register",
                                "Result": 1,
                                "Error": None,
                                "RuleResult": [
                                    {
                                        "Result": 3,
                                        "PotName": "Fail",
                                        "PotAmount": 0,
                                        "AlertMessage": ""
                                    },
                                    {
                                        "Result": 1,
                                        "PotName": "Not Matched",
                                        "PotAmount": 1,
                                        "AlertMessage": None
                                    }
                                ],
                                "RawResults": "[]",
                                "FullOutput": [
                                    {
                                        "CheckOutput": {
                                            "id": "VMC",
                                            "on_halo_level_10": "0",
                                            "on_halo_level_9": "0",
                                            "on_halo_level_8": "0",
                                            "on_halo_level_7": "0",
                                            "on_halo_level_6": "0",
                                            "on_halo_level_5": "0",
                                            "on_halo_level_4": "0",
                                            "on_halo_level_3": "0",
                                            "on_halo_level_2": "0",
                                            "on_halo_level_1": "0",
                                            "on_halo_level_other": "0",
                                            "info_found": "0",
                                            "highest_level_found": "0",
                                            "lowest_level_found": "0"
                                        },
                                        "FilterOutput": [
                                            {
                                                "FilterCode": "HaloLevel10",
                                                "Key": None,
                                                "Parameter": "1",
                                                "Matched": {
                                                    "on_halo_level_10": False
                                                }
                                            }
                                        ]
                                    }
                                ]
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
                                                ],
                                                'count': 1
                                            },
                                            {
                                                'database_name': 'Credit Bureau',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ],
                                                'count': 1
                                            },
                                            {
                                                'database_name': 'Death Register',
                                                'database_type': 'MORTALITY',
                                                'matched_fields': [],
                                                'count': 0
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
                    },
                    {
                        "Name": "Stage2",
                        "Conditions": [
                            {
                                "If": 1,
                                "Then": 0,
                                "NextStageIndex": 3
                            },
                            {
                                "If": 2,
                                "Then": 1,
                                "NextStageIndex": 3
                            }
                        ],
                        "StageResult": 1,
                        "CheckResults": [
                            {
                                "Rules": [
                                    {
                                        "CheckFilters": [
                                            {
                                                "RuleId": 2297,
                                                "CheckFilterId": 10,
                                                "FilterShortCode": "HaloLevel10",
                                                "FilterParameter": {
                                                    "Key": None,
                                                    "Value": "1"
                                                }
                                            }
                                        ],
                                        "FilterShortCode": "HaloLevel10",
                                        "FilterParameter": "1",
                                        "Comparator": 0,
                                        "CheckAmount": 0,
                                        "RuleResult": 2,
                                        "PotName": "Fail",
                                        "LastUpdatedDate": "2016-11-22T16:27:08Z"
                                    },
                                    {
                                        "CheckFilters": [
                                            {
                                                "RuleId": 2300,
                                                "CheckFilterId": 10,
                                                "FilterShortCode": "HaloLevel10",
                                                "FilterParameter": {
                                                    "Key": None,
                                                    "Value": "1"
                                                }
                                            }
                                        ],
                                        "FilterShortCode": "HaloLevel10",
                                        "FilterParameter": "1",
                                        "Comparator": 2,
                                        "CheckAmount": 0,
                                        "RuleResult": 1,
                                        "PotName": "Not Matched",
                                        "AlertMessage": None,
                                        "LastUpdatedDate": "2016-11-22T16:27:08Z"
                                    }
                                ],
                                "StageName": "Stage2",
                                "CheckName": "Death Register",
                                "Result": 3,
                                "Error": None,
                                "RuleResult": [
                                    {
                                        "Result": 3,
                                        "PotName": "Fail",
                                        "PotAmount": 0,
                                        "AlertMessage": ""
                                    },
                                    {
                                        "Result": 1,
                                        "PotName": "Not Matched",
                                        "PotAmount": 1,
                                        "AlertMessage": None
                                    }
                                ],
                                "RawResults": "[]",
                                "FullOutput": [
                                    {
                                        "CheckOutput": {
                                            "id": "VMC",
                                            "on_halo_level_10": "0",
                                            "on_halo_level_9": "0",
                                            "on_halo_level_8": "0",
                                            "on_halo_level_7": "0",
                                            "on_halo_level_6": "0",
                                            "on_halo_level_5": "0",
                                            "on_halo_level_4": "0",
                                            "on_halo_level_3": "0",
                                            "on_halo_level_2": "0",
                                            "on_halo_level_1": "0",
                                            "on_halo_level_other": "0",
                                            "info_found": "0",
                                            "highest_level_found": "0",
                                            "lowest_level_found": "0"
                                        },
                                        "FilterOutput": [
                                            {
                                                "FilterCode": "HaloLevel10",
                                                "Key": None,
                                                "Parameter": "1",
                                                "Matched": {
                                                    "on_halo_level_10": True
                                                }
                                            }
                                        ]
                                    }
                                ]
                            }
                        ]
                    }
                ],
                "Error": ""
            }
        }
    }

    response_body = capita_to_passfort_data(capita_data)
    print(response_body)
    assert response_body == {
                                "output_data": {
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Role',
                                                'database_type': 'CIVIL',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ],
                                                'count': 1
                                            },
                                            {
                                                'database_name': 'Credit Bureau',
                                                'database_type': 'CREDIT',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "DOB"
                                                ],
                                                'count': 1
                                            },
                                            {
                                                'database_name': 'Death Register',
                                                'database_type': 'MORTALITY',
                                                'matched_fields': [
                                                    "FORENAME",
                                                    "SURNAME",
                                                    "ADDRESS"
                                                ],
                                                'count': 1
                                            }
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
                                "errors": [{'code': 101, 'message': f'Provider Error: Please validate Applicant Detail, '
                                                                    f'mandatory field missing (house number, postal '
                                                                    f'code or date of birth).'}]
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
