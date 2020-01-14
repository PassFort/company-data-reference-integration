import pytest
from copy import deepcopy
from lexisnexis.convert_data import passfort_to_lexisnexis_data

BASE_REQUEST = {
    'InstantIDRequest': {
        'Options': {
            'DOBMatch': {
                'MatchType': 'FuzzyCCYYMMDD'
            },
            'IncludeModels': {
                'FraudPointModel': {'IncludeRiskIndices': True}
            },
            'NameInputOrder': 'Unknown'
        },
        'SearchBy': {},
        'User': {'DLPurpose': '3', 'GLBPurpose': '5'}
    }
}


def test_empty_package(client):
    lexisnexis_request_data = passfort_to_lexisnexis_data({})

    assert lexisnexis_request_data == BASE_REQUEST


def test_empty_input_data(client):
    lexisnexis_request_data = passfort_to_lexisnexis_data({'input_data': None})

    assert lexisnexis_request_data == BASE_REQUEST


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
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Name': {
            'First': 'Todd'
        }
    }
    assert lexisnexis_request_data == output_data


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
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Name': {
            'First': 'Todd',
            'Middle': 'Astor'
        }
    }
    assert lexisnexis_request_data == output_data


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
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Name': {
            'First': 'Todd',
            'Middle': 'Astor Royal Tony'
        }
    }
    assert lexisnexis_request_data == output_data


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
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Name': {
            'Last': 'Stark'
        }
    }
    assert lexisnexis_request_data == output_data


def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'DOB': {
            'Year': 2019,
            'Month': 1,
            'Day': 31
        }
    }
    assert lexisnexis_request_data == output_data


def test_dob_year_month(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'DOB': {
            'Year': 2019,
            'Month': 1
        }
    }
    assert lexisnexis_request_data == output_data


def test_dob_year(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'DOB': {
            'Year': 2019
        }
    }
    assert lexisnexis_request_data == output_data


def test_gender(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Gender': 'M'
    }
    assert lexisnexis_request_data == output_data


def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': {}
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    assert lexisnexis_request_data == BASE_REQUEST


def test_one_simple_address(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    "address": {
                        "postal_code": "12345",
                        "street_number": "10",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Address': {
            'Zip5': "12345",
            'StreetAddress1': "10"
        }
    }
    assert lexisnexis_request_data == output_data


def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    "address": {
                        "street_number": "10",
                        "premise": 'My building',
                        "subpremise": '0',
                        "route": "Downing St",
                        "postal_town": 'MORNING VIEW',
                        "state_province": 'KY',
                        "postal_code": "12345",
                        "type": "STRUCTURED",
                    }
                }
            ]
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Address': {
            'Zip5': "12345",
            'StreetAddress1': "10 Downing St My building 0",
            'City': 'MORNING VIEW',
            'State': 'KY'
        }
    }
    assert lexisnexis_request_data == output_data


def test_communication_with_empty_values(client):
    input_data = {
        'input_data': {
            'contact_details': {}
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    assert lexisnexis_request_data == BASE_REQUEST


def test_communication_with_email(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Email': 'test@test.com'
    }
    assert lexisnexis_request_data == output_data


def test_communication_with_telephone(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'phone_number': '+44 7911 123456'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'HomePhone': '+44 7911 123456',
        'WorkPhone': '+44 7911 123456'
    }
    assert lexisnexis_request_data == output_data


def test_communication_with_full_values(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com',
                'phone_number': '+44 7911 123456'
            }
        }
    }
    lexisnexis_request_data = passfort_to_lexisnexis_data(input_data)
    output_data = deepcopy(BASE_REQUEST)
    output_data['InstantIDRequest']["SearchBy"] = {
        'Email': 'test@test.com',
        'HomePhone': '+44 7911 123456',
        'WorkPhone': '+44 7911 123456'
    }
    assert lexisnexis_request_data == output_data
