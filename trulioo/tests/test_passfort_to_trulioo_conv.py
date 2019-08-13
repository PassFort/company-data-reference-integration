import pytest 

from trulioo.convert_data import passfort_to_trulioo_data

def test_empty_package(client):
    truilioo_request_data, country_code = passfort_to_trulioo_data({})

    assert truilioo_request_data == {}
    assert country_code == 'GB'

def test_empty_input_data(client):
    truilioo_request_data, country_code = passfort_to_trulioo_data({'input_data':None})

    assert truilioo_request_data == {}
    assert country_code == 'GB'

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
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            "FirstGivenName": 'Todd'
        }
    }
    assert truilioo_request_data == output_data


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
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstGivenName': 'Todd',
            'MiddleName':'Astor'
        }
    }
    assert truilioo_request_data == output_data

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
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstGivenName': 'Todd',
            'MiddleName':'Astor Royal Tony'
        }
    }
    assert truilioo_request_data == output_data

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
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstSurName': 'Stark'
        }
    }
    assert truilioo_request_data == output_data

def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019,
            'MonthOfBirth': 1,
            'DayOfBirth': 31
        }
    }
    assert truilioo_request_data == output_data

def test_dob_year_month(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019,
            'MonthOfBirth': 1
        }
    }
    assert truilioo_request_data == output_data

def test_dob_year(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019
        }
    }
    assert truilioo_request_data == output_data

def test_gender(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'Gender': 'M'
        }
    }
    assert truilioo_request_data == output_data

def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': {}
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {}
    assert truilioo_request_data == output_data


def test_one_simple_address(client):
    input_data = {
        'input_data': {
            'address_history': {
                "current": {    
                    "country": "GBR",
                    "postal_code": "SW1A 2AA",
                    "street_number": "10",
                    "type": "STRUCTURED"
                }
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location':{
            'BuildingNumber':'10',
            'PostalCode':'SW1A 2AA'
        }
    }
    assert truilioo_request_data == output_data

def test_one_simple_address_diff_country(client):
    input_data = {
        'input_data': {
            'address_history': {
                "current": {
                    "country": "BRA",
                    "postal_code": "SW1A 2AA",
                    "street_number": "10",
                    "type": "STRUCTURED"
                }
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location':{
            'BuildingNumber':'10',
            'PostalCode':'SW1A 2AA'
        }
    }
    assert truilioo_request_data == output_data
    assert country_code == 'BR'

def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history': {
                "current": {
                    "country": "GBR",
                    "street_number": "10",
                    "premise": 'My building',
                    "subpremise" : '0',
                    "route": "Downing St",
                    "postal_town": "London",
                    "locality": 'Westminster',
                    "county": 'City of London',
                    "state_province": 'Greater London',
                    "postal_code": "SW1A 2AA",
                    "type": "STRUCTURED",
                }
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location':{
            'BuildingNumber':'10',
            'BuildingName': 'My building',
            'UnitNumber': '0',
            'StreetName': 'Downing St',
            'City': 'London',
            'Suburb': 'Westminster',
            'County': 'City of London',
            'StateProvinceCode': 'Greater London',
            'PostalCode':'SW1A 2AA'
        }
    }
    assert truilioo_request_data == output_data

def test_communication_with_empty_values(client):
    input_data = {
        'input_data': {
            'contact_details': {}
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {}
    assert truilioo_request_data == output_data

def test_communication_with_email(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'EmailAddress': 'test@test.com'
        }
    }
    assert truilioo_request_data == output_data

def test_communication_with_telephone(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'phone_number': '+44 7911 123456'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'Telephone': '+44 7911 123456'
        }
    }
    assert truilioo_request_data == output_data

def test_communication_with_full_values(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com',
                'phone_number': '+44 7911 123456'
            }
        }
    }
    truilioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'EmailAddress': 'test@test.com',
            'Telephone': '+44 7911 123456'
        }
    }
    assert truilioo_request_data == output_data

