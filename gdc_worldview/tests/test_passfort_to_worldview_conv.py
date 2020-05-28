import pytest 
from copy import deepcopy
from worldview.convert_data import passfort_to_worldview_data

def test_empty_package(client):
    worldview_request_data = passfort_to_worldview_data({})

    assert worldview_request_data == {}
    
def test_empty_input_data(client):
    worldview_request_data = passfort_to_worldview_data({'input_data':None})
    assert worldview_request_data == {}

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
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'identity': {
            'givenfullname': 'Todd'
        }
    }
    assert worldview_request_data == output_data


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
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'identity': {
            'givenfullname': 'Todd'
        }
    }
    assert worldview_request_data == output_data

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
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'identity': {
            'givenfullname': 'Todd'
        }
    }
    assert worldview_request_data == output_data

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
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'identity': {
            'surnameFirst': 'Stark'
        }
    }
    assert worldview_request_data == output_data

def test_many_names_with_surname(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'name': {
                    'given_names': ['Todd', 'Astor', 'Royal', 'Tony'],
                    'family_name': 'Stark'
                }
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'identity': {
            'givenfullname': 'Todd',
            'surnameFirst': 'Stark',
            'completename': 'Todd Astor Royal Tony Stark'
        }
    }
    assert worldview_request_data == output_data

def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        "identity": {
            "dob": "01/31/2019"
        }
    }
    assert worldview_request_data == output_data

def test_dob_year_month(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01'
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        "identity": {
            "dob": "01/2019"
        }
    }
    assert worldview_request_data == output_data

def test_dob_year(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019'
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        "identity": {
            "dob": "2019"
        }
    }
    assert worldview_request_data == output_data

def test_gender(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        "identity": {
            "gender": "M"
        }
    }
    assert worldview_request_data == output_data

def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': {}
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    assert worldview_request_data == {}


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
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'address': {
            'houseNumber': '10', 
            'postalCode': '12345'
        }
    }
    assert worldview_request_data == output_data


def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history':[
                {
                    "address": {
                        "premise": 'My building',
                        "street_number": 'street 23',
                        "route": "St. Jonh",
                        "subpremise" : '10',
                        'locality': 'Neverland',
                        "postal_town": 'MORNING VIEW',
                        "postal_code": "12345",
                        'state_province': 'Test',
                        'country': 'GBR',
                        "type": "STRUCTURED",
                    }
                }
            ]
        }
    }

    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
            'address': {
                'addressLine1': 'street 23 St. Jonh My building',
                'houseNumber': '10',
                'locality': 'Neverland',
                'postalCode': '12345',
                'district': 'MORNING VIEW',
                'province': 'Test',
                'countryCode': 'GB'
            }
    }
    assert worldview_request_data == output_data

def test_communication_with_empty_values(client):
    input_data = {
        'input_data': {
            'contact_details': {}
        }
    }

    worldview_request_data = passfort_to_worldview_data(input_data)
    
    output_data = {}
    assert worldview_request_data == output_data
    
def test_communication_with_email(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com'
            }
        }
    }

    worldview_request_data = passfort_to_worldview_data(input_data)

    output_data = {
        'email': { 
            'fullEmailAddress': 'test@test.com' 
        }
    }
    assert worldview_request_data == output_data

def test_communication_with_telephone(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'phone_number': '+44 7911 123456'
            }
        }
    }
    
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'phone': { 
            'phoneNumber': '+44 7911 123456'
        }
    }
    assert worldview_request_data == output_data


def test_communication_with_full_values(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com',
                'phone_number': '+44 7911 123456'
            }
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    
    output_data = {
        'phone': { 
            'phoneNumber': '+44 7911 123456'
        },
        'email': { 
            'fullEmailAddress': 'test@test.com' 
        }
    }
    assert worldview_request_data == output_data


def test_identity_number_for_current_country(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'national_identity_number': {
                    'MEX': 'MEX_ID',
                    'GBR': 'GBR_ID'
                }
            },
            'address_history': [
                {
                    "address": {
                        "country": "GBR",
                        "postal_code": "12345",
                        "subpremise": "10",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'address': {
            'houseNumber': '10',
            'postalCode': '12345',
            'countryCode': 'GB',
        },
        'identity': {
            'nationalid': 'GBR_ID'
        }
    }
    assert worldview_request_data == output_data

def test_identity_number_for_other_countries_are_not_sent(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'national_identity_number': {
                    'MEX': 'MEX_ID',
                    'USA': 'USA_ID'
                }
            },
            'address_history':[
                {
                    "address": {
                        "country": "GBR",
                        "postal_code": "12345",
                        "subpremise": "10",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    worldview_request_data = passfort_to_worldview_data(input_data)
    output_data = {
        'address': {
            'houseNumber': '10',
            'postalCode': '12345',
            'countryCode': 'GB',
        }
    }
    assert worldview_request_data == output_data