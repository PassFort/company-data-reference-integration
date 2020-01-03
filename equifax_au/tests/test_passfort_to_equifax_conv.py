import pytest 
import json
from equifax.convert_data import passfort_to_equifax_data
from equifax.convert_data import xml_to_dict_response

def xml_to_dict(xml):
    order_dict = xml_to_dict_response(xml)
    return json.loads(json.dumps(order_dict))

CREDENTIALS = {
    'credentials' :{
        'username': 'dummy_user',
        'password': 'dummy_pass',
        'url': 'dummy_endpoint'}}

def test_empty_data_package(client):
    equifax_request_data = passfort_to_equifax_data(CREDENTIALS)

    assert list(xml_to_dict(equifax_request_data).keys()) == ['idm:request']

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
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)

    assert list(xml_to_dict(equifax_request_data)['idm:request'].keys()) == ['@client-reference', '@reason-for-enquiry', 'idm:consents', 'idm:individual-name']
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:individual-name'] == {'idm:first-given-name' :'Todd' }
    

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
    input_data.update(CREDENTIALS)
    
    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        'idm:first-given-name': 'Todd',
        'idm:other-given-name': 'Astor'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:individual-name'] == output_data

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
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        'idm:first-given-name': 'Todd',
        'idm:other-given-name': 'Astor Royal Tony'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:individual-name'] == output_data

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
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        'idm:family-name': 'Stark'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:individual-name'] == output_data

def test_dob_complete(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'dob': '2019-01-31'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:date-of-birth'] == '2019-01-31'

def test_gender_male(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'M'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:gender'] == 'male'

def test_gender_female(client):
    input_data = {
        'input_data': {
            'personal_details': {
                'gender': 'F'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:gender'] == 'female'

def test_empty_address_history(client):
    input_data = {
        'input_data': {
            'address_history': []
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    assert 'idm:current-address' not in xml_to_dict(equifax_request_data)['idm:request'].keys()

def test_one_simple_address(client):
    input_data = {
        'input_data': {
            'address_history':[
                {
                    "address": {    
                        "country": "GBR",
                        "postal_code": "SW1A 2AA",
                        "street_number": "10",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        #'idm:country': 'GBR', 
        'idm:postcode': 'SW1A 2AA', 
        'idm:street-number': '10'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:current-address'] == output_data

def test_two_address(client):
    input_data = {
        'input_data': {
            'address_history':[
                {
                    "address": {    
                        "country": "GBR",
                        "postal_code": "SW1A 2AA",
                        "street_number": "10",
                        "type": "STRUCTURED"
                    }
                },
                {
                    "address": {    
                        "country": "GBR-old",
                        "postal_code": "SW1A 2AA-old",
                        "street_number": "10-old",
                        "type": "STRUCTURED"
                    }
                }
            ]
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    current_address = {
        #'idm:country': 'GBR', 
        'idm:postcode': 'SW1A 2AA', 
        'idm:street-number': '10'
    }
    previous_address = {
        #'idm:country': 'GBR-old', 
        'idm:postcode': 'SW1A 2AA-old', 
        'idm:street-number': '10-old'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:current-address'] == current_address
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:previous-address'] == previous_address


# def test_one_simple_address_diff_country(client):
#     input_data = {
#         'input_data': {
#             'address_history': [
#                 {
#                     "address": {
#                         "country": "BRA",
#                         "postal_code": "SW1A 2AA",
#                         "street_number": "10",
#                         "type": "STRUCTURED"
#                     }
#                 }
#             ]
#         }
#     }
#     input_data.update(CREDENTIALS)

#     equifax_request_data = passfort_to_equifax_data(input_data)
#     output_data = {
#         'idm:country': 'BRA', 
#         'idm:postcode': 'SW1A 2AA', 
#         'idm:street-number': '10'
#     }
#     assert xml_to_dict(equifax_request_data)['idm:request']['idm:current-address'] == output_data

def test_one_complete_address(client):
    input_data = {
        'input_data': {
            'address_history': [
                {
                    "address": {
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
            ]
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        #'idm:country': 'GBR',
        'idm:postcode': 'SW1A 2AA',
        'idm:property': 'My building',
        'idm:state': 'Greater London',
        'idm:street-name': 'Downing St',
        'idm:street-number': '10',
        'idm:suburb': 'Westminster',
        'idm:unit-number': '0'
    }
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:current-address'] == output_data


def test_communication_with_empty_values(client):
    input_data = {
        'input_data': {
            'contact_details': {}
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    
    request_keys = xml_to_dict(equifax_request_data)['idm:request'].keys()
    assert 'idm:email-address' not in request_keys
    assert 'idm:phone' not in request_keys
    
def test_communication_with_email(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:email-address'] == 'test@test.com'

def test_communication_with_telephone(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'phone_number': '+44 7911 123456'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    output_data = {
        'idm:numbers': {
            'idm:mobile-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            },
            'idm:work-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            },
            'idm:home-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            }
        }
    }
    print(xml_to_dict(equifax_request_data)['idm:request']['idm:phone'])
    assert xml_to_dict(equifax_request_data)['idm:request']['idm:phone'] == output_data


def test_communication_with_full_values(client):
    input_data = {
        'input_data': {
            'contact_details': {
                'email': 'test@test.com',
                'phone_number': '+44 7911 123456'
            }
        }
    }
    input_data.update(CREDENTIALS)

    equifax_request_data = passfort_to_equifax_data(input_data)
    phone_output_data = {
        'idm:numbers': {
            'idm:mobile-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            },
            'idm:work-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            },
            'idm:home-phone-number': {
                '#text': '+44 7911 123456',
                '@verify': "1"
            }
        }
    }
    idm_request = xml_to_dict(equifax_request_data)['idm:request']
    assert idm_request['idm:email-address'] == 'test@test.com'
    assert idm_request['idm:phone'] == phone_output_data

