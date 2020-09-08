import pytest
from copy import deepcopy
from capita.convert_data import passfort_to_capita_data

def test_empty_package(client):
    capita_request_data = passfort_to_capita_data({})

    assert capita_request_data == {}

def test_empty_input_data(client):
    capita_request_data = passfort_to_capita_data({'input_data':None})
    assert capita_request_data == {}

def test_single_name_without_surname(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd']
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Forename": "Todd"
        }
    }
    assert capita_request_data == output_data


def test_two_names_without_surname(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Astor']
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Forename": "Todd",
            "Secondname": "Astor"
        }
    }
    assert capita_request_data == output_data

def test_many_names_without_surname(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Astor', 'Royal', 'Tony']
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Forename": "Todd",
            "Secondname": "Astor Royal Tony"
        }
    }
    assert capita_request_data == output_data

def test_just_surname(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'family_name': 'Stark'
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Surname": "Stark"
        }
    }
    assert capita_request_data == output_data

def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Date_Of_Birth": "2019-01-31"
        }
    }
    assert capita_request_data == output_data

def test_dob_year_month(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01'
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Date_Of_Birth": "2019-01"
        }
    }
    assert capita_request_data == output_data

def test_dob_year(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019'
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Date_Of_Birth": "2019"
        }
    }
    assert capita_request_data == output_data

def test_gender(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Person": {
            "Gender": "M"
        }
    }
    assert capita_request_data == output_data

def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': {}
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    assert capita_request_data == {}


def test_one_simple_address(client):
    input_data = {
        'input_data': {
            'address_history':[
                {
                    "address": {
                        "postal_code": "12345",
                        "subpremise": "10",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Address": [
            {
                'PostCode': '12345',
                'HouseNumber': '10'
            }
        ]
    }
    assert capita_request_data == output_data


def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history':[
                {
                    "address": {
                        "premise": 'My building',
                        "subpremise" : '10',
                        "postal_town": 'MORNING VIEW',
                        "postal_code": "12345",
                        "type": "STRUCTURED",
                    }
                }
            ]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        "Address": [
            {
                'PostCode': '12345',
                'HouseName': 'My building',
                'HouseNumber': '10',
                'PostTown': 'MORNING VIEW'
            }
        ]
    }
    assert capita_request_data == output_data


def test_driving_licence_without_country_code_should_be_ignored(client):
    input_data = {
        'input_data': {
            'documents_metadata': [{
                'document_type': 'DRIVING_LICENCE',
                'number': '123456',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    assert capita_request_data == {}


def test_driving_licence_with_gbr_country_code(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'family_name': 'Jones'
                }
            },
            'documents_metadata': [{
                'document_type': 'DRIVING_LICENCE',
                'number': '123456',
                'country_code': 'GBR',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        'Person': {
            'Surname': 'Jones',
            'DrivingLicenceNo': '123456'
        }
    }
    assert capita_request_data == output_data


def test_driving_licence_with_country_code(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'family_name': 'Jones'
                }
            },
            'documents_metadata': [{
                'document_type': 'DRIVING_LICENCE',
                'number': '123456',
                'country_code': 'ITA',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    assert capita_request_data == {
        'Person': {
            'Surname': 'Jones'
        }
    }


def test_id_card_without_country_code_should_be_ignored(client):
    input_data = {
        'input_data': {
            'documents_metadata': [{
                'document_type': 'STATE_ID',
                'number': '456789',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    assert capita_request_data == {}


def test_id_card_eu_country_code(client):
    input_data = {
        'input_data': {
            'documents_metadata': [{
                'document_type': 'STATE_ID',
                'number': '456789',
                'country_code': 'DEU',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    output_data = {
        'EuropeanIDCardNo': '456789',
    }
    assert capita_request_data == output_data


def test_id_card_non_eu_country_code(client):
    input_data = {
        'input_data': {
            'documents_metadata': [{
                'document_type': 'STATE_ID',
                'number': '456789',
                'country_code': 'BRA',
            }]
        }
    }
    capita_request_data = passfort_to_capita_data(input_data)
    assert capita_request_data == {}


def test_national_id_number(client):
    check_data = {
        'input_data': {
            'personal_details': {
                'national_identity_number': {
                    "GBR": "123456"
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(check_data)
    expected = {
        'Person': {
            'PersonalNumber': '123456'
        }
    }
    assert capita_request_data == expected


def test_other_national_id_number(client):
    check_data = {
        'input_data': {
            'personal_details': {
                'national_identity_number': {
                    "USA": "123456"
                }
            }
        }
    }
    capita_request_data = passfort_to_capita_data(check_data)
    assert capita_request_data == {"Person": {}}
