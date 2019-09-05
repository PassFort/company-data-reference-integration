import pytest 

from trulioo.convert_data import trulioo_to_passfort_data

def test_empty_package(client):
    response_body = trulioo_to_passfort_data({})

    assert response_body == {
                                "output_data": {
                                },
                                "raw": {},
                                "errors": []
                            }

def test_record_with_empty_datasource_results(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [], 
            'Errors': []
        }, 
        'Errors': []
    }

    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }    

def test_record_with_one_datasource_without_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstInitial', 
                            'Status': 'nomatch'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }    

def test_record_with_one_datasource_with_surname_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  


def test_record_with_one_datasource_with_forename_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstGivenName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['FORENAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  


def test_record_with_one_datasource_with_dob_complete_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'DayOfBirth', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'MonthOfBirth', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }

    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  

def test_record_with_one_datasource_with_dob_year_month_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'MonthOfBirth', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }

    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  


def test_record_with_one_datasource_with_dob_year_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'YearOfBirth', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }

    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['DOB']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  


def test_record_with_one_datasource_with_dob_day_nomatch(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'DayOfBirth', 
                            'Status': 'nomatch'
                        },
                        {
                            'FieldName': 'MonthOfBirth', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }

    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": []
                            }  

def test_record_with_one_datasource_with_address_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'BuildingNumber', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['ADDRESS']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  

def test_record_with_one_datasource_with_address_match_full_fields(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'BuildingNumber', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingName', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'UnitNumber', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StreetName', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'City', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'Suburb', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'County', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StateProvinceCode', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'PostalCode', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['ADDRESS']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  

def test_record_with_one_datasource_with_address_nomatch_by_partial_fields(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstGivenName', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingNumber', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingName', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'UnitNumber', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StreetName', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'City', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'Suburb', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'County', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StateProvinceCode', 
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'PostalCode', 
                            'Status': 'nomatch'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['FORENAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  

def test_record_with_one_datasource_with_database_type_credit(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            }  


def test_record_with_one_datasource_with_database_type_civil(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Electoral Roll', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Electoral Roll',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['SURNAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            } 


def test_record_with_two_datasource_with_diff_database_type(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                },
                {
                    'DatasourceName': 'Electoral Roll', 
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName', 
                            'Status': 'match'
                        }
                    ], 
                    'Errors': [], 
                    'FieldGroups': []
                }, 
            ], 
            'Errors': []
        }, 
        'Errors': []
    }
    
    response_body = trulioo_to_passfort_data(trulioo_data)

    assert response_body == {
                                "output_data": {
                                    'entity_type': 'INDIVIDUAL',
                                    'electronic_id_check': {
                                        'matches': [
                                            {
                                                'database_name': 'Credit Agency',
                                                'database_type': 'CREDIT',
                                                'matched_fields': ['SURNAME']
                                            },
                                            {
                                                'database_name': 'Electoral Roll',
                                                'database_type': 'CIVIL',
                                                'matched_fields': ['SURNAME']
                                            }
                                        ]
                                    }
                                },
                                "raw": trulioo_data,
                                "errors": []
                            } 

def test_record_error_missing_required_fields_1001(client):
    trulioo_data = {'Errors': [{'Code': '1001'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 101, 'message': 'Missing required fields'}]
                            } 

def test_record_error_missing_required_fields_4001(client):
    trulioo_data = {'Errors': [{'Code': '4001'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 101, 'message': 'Missing required fields'}]
                            } 

def test_record_error_missing_required_fields_3005(client):
    trulioo_data = {'Errors': [{'Code': '3005'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 101, 'message': 'Missing required fields'}]
                            } 

def test_record_error_missing_required_fields_not_duplicated(client):
    trulioo_data = {'Errors': [{'Code': '1001'}, {'Code': '4001'}, {'Code': '3005'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 101, 'message': 'Missing required fields'}]
                            } 

def test_record_error_unknown_error(client):
    trulioo_data = {'Errors': [{'Code': '2000'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 401, 'message': 'Unknown internal error'}]
                            } 

def test_record_error_invalid_input_data_1006(client):
    trulioo_data = {'Errors': [{'Code': '1006'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{
                                    'code': 201, 
                                    'message': 'The submitted data was invalid. Provider returned error code 1006'
                                }]
                            }

def test_record_error_invalid_input_data_1008(client):
    trulioo_data = {'Errors': [{'Code': '1008'}]}
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{
                                    'code': 201, 
                                    'message': 'The submitted data was invalid. Provider returned error code 1008'
                                }]
                            }

def test_record_error_missing_required_fields_1001_datasource_error(client):
    trulioo_data = {
        "Record": {
            "DatasourceResults": [
                {
                    "DatasourceName": "Credit Agency",
                    "Errors": [{"Code": "1001","Message": "Missing required field: FirstSurName"}]
                }
            ]
        }
    }
    response_body = trulioo_to_passfort_data(trulioo_data)
    assert response_body == {
                                "output_data": {},
                                "raw": trulioo_data,
                                "errors": [{'code': 101, 'message': 'Missing required fields'}]
                            } 