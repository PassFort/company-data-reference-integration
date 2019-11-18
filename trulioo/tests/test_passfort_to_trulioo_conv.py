import pytest

from trulioo.convert_data import passfort_to_trulioo_data


def test_empty_package(client):
    trulioo_request_data, country_code = passfort_to_trulioo_data({})

    assert trulioo_request_data == {}
    assert country_code == 'GB'


def test_empty_input_data(client):
    trulioo_request_data, country_code = passfort_to_trulioo_data(
        {'input_data': None})

    assert trulioo_request_data == {}
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
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            "FirstGivenName": 'Todd'
        }
    }
    assert trulioo_request_data == output_data


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
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstGivenName': 'Todd',
            'MiddleName': 'Astor'
        }
    }
    assert trulioo_request_data == output_data


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
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstGivenName': 'Todd',
            'MiddleName': 'Astor Royal Tony'
        }
    }
    assert trulioo_request_data == output_data


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
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'FirstSurName': 'Stark'
        }
    }
    assert trulioo_request_data == output_data


def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019,
            'MonthOfBirth': 1,
            'DayOfBirth': 31
        }
    }
    assert trulioo_request_data == output_data


def test_dob_year_month(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019,
            'MonthOfBirth': 1
        }
    }
    assert trulioo_request_data == output_data


def test_dob_year(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'YearOfBirth': 2019
        }
    }
    assert trulioo_request_data == output_data


def test_gender(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'PersonInfo': {
            'Gender': 'M'
        }
    }
    assert trulioo_request_data == output_data


def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': []
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {}
    assert trulioo_request_data == output_data


def test_one_simple_address(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    'address': {
                        "country": "GBR",
                        "postal_code": "SW1A 2AA",
                        "street_number": "10",
                        "type": "STRUCTURED"
                    },
                },
            ]
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location': {
            'BuildingNumber': '10',
            'PostalCode': 'SW1A 2AA'
        }
    }
    assert trulioo_request_data == output_data


def test_one_simple_address_diff_country(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    'address': {
                        "country": "BRA",
                        "postal_code": "SW1A 2AA",
                        "street_number": "10",
                        "type": "STRUCTURED"
                    },
                },
            ]
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location': {
            'BuildingNumber': '10',
            'PostalCode': 'SW1A 2AA'
        }
    }
    assert trulioo_request_data == output_data
    assert country_code == 'BR'


def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    'address': {
                        "country": "GBR",
                        "street_number": "10",
                        "premise": 'My building',
                        "subpremise": '0',
                        "route": "Downing St",
                        "postal_town": "Westminster",
                        "locality": 'London',
                        "county": 'City of London',
                        "state_province": 'Greater London',
                        "postal_code": "SW1A 2AA",
                        "type": "STRUCTURED",
                    },
                }
            ],
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Location': {
            'BuildingNumber': '10',
            'BuildingName': 'My building',
            'UnitNumber': '0',
            'StreetName': 'Downing St',
            'City': 'London',
            'Suburb': 'Westminster',
            'County': 'City of London',
            'StateProvinceCode': 'Greater London',
            'PostalCode': 'SW1A 2AA'
        }
    }
    assert trulioo_request_data == output_data


def test_communication_with_empty_values(client):
    input_data = {
        'input_data': {
            'contact_details': {}
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {}
    assert trulioo_request_data == output_data


def test_communication_with_email(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'EmailAddress': 'test@test.com'
        }
    }
    assert trulioo_request_data == output_data


def test_communication_with_telephone(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'phone_number': '+44 7911 123456'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'Telephone': '+44 7911 123456'
        }
    }
    assert trulioo_request_data == output_data


def test_communication_with_full_values(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com',
                'phone_number': '+44 7911 123456'
            }
        }
    }
    trulioo_request_data, country_code = passfort_to_trulioo_data(input_data)
    output_data = {
        'Communication': {
            'EmailAddress': 'test@test.com',
            'Telephone': '+44 7911 123456'
        }
    }
    assert trulioo_request_data == output_data
