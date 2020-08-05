import pytest
from unittest.mock import Mock, patch

def test_health_check_get_method(client):
    response = client.get("/health")
    assert response.status_code == 200

def test_address_geocode_check_empty_body(client):
    body = {}
    response = client.post("/check", json=body)

    expected_code = 205
    expected_message = "Provider Configuration Error: 'Credentials is required' while running the 'Loqate' service"

    assert response.status_code == 400
    assert response.json["code"] == expected_code
    assert response.json["message"] == expected_message

def test_address_geocode_check_no_apikey(client):
    body = {
        "credentials": {},
    }
    response = client.post("/check", json=body)

    expected_code = 205
    expected_message = "Provider Configuration Error: 'Apikey is required' while running the 'Loqate' service"

    assert response.status_code == 400
    assert response.json["message"] == expected_message
    assert response.json["code"] == expected_code

def test_address_geocode_check_no_input(client):
    body = {
        "credentials": {
            "apikey": "test"
        },
        "input_data": {},
    }
    response = client.post("/check", json=body)

    expected = {
        "code": 201,
        "info": {
            "input_data": {
                "address": [
                    "This field is required."
                ]
            }
        },
        "message": "Bad API request",
        "source": "API"
    }

    assert response.status_code == 400
    assert response.json == expected

def test_address_geocode_check_validates_input(client):
    body = {
        "credentials": {
            "apikey": "test"
        },
        "input_data": {"address": {}},
    }
    response = client.post("/check", json=body)

    expected = {
        "code": 201,
        "info": {
            "input_data": {
                "address": {
                    "country": [
                        "This field is required."
                    ],
                    "type": [
                        "This field is required."
                    ]
                }
            }
        },
        "message": "Bad API request",
        "source": "API"
    }

    assert response.status_code == 400
    assert response.json == expected

happy_response = [{
    "Input": {
        "Country": "GBR",
        "Premise": "Imperial House 12-14",
        "Locality": "Aberdeen",
        "PostalCode": "AB11 6PH",
        "SubAdministrativeArea": "Aberdeen City"
    },
    "Matches": [{
        "AdministrativeArea": "Aberdeenshire",
        "Building": "Imperial House 12-14",
        "CountryName": "United Kingdom",
        "DeliveryAddress": "Imperial House 12-14, Exchange Street",
        "DeliveryAddress1": "Imperial House 12-14",
        "DeliveryAddress2": "Exchange Street",
        "GeoAccuracy": "A3",
        "GeoDistance": "100.1",
        "HyphenClass": "B",
        "ISO3166-2": "GB",
        "Country": "GB",
        "ISO3166-3": "GBR",
        "Latitude": "57.145618",
        "Locality": "Aberdeen",
        "Longitude": "-2.096897",
        "MatchRuleLabel": "Rlfnp",
        "PostalCode": "AB11 6PH",
        "PostalCodePrimary": "AB11 6PH",
        "Thoroughfare": "Exchange Street"
    }]
}]

no_geocode_response = [{
    "Input": {
        "Country": "GBR",
        "Premise": "Imperial House 12-14",
        "Locality": "Aberdeen",
        "PostalCode": "AB11 6PH",
        "SubAdministrativeArea": "Aberdeen City"
    },
    "Matches": [{
        "AdministrativeArea": "Aberdeenshire",
        "Building": "Imperial House 12-14",
        "CountryName": "United Kingdom",
        "DeliveryAddress": "Imperial House 12-14, Exchange Street",
        "DeliveryAddress1": "Imperial House 12-14",
        "DeliveryAddress2": "Exchange Street",
        "HyphenClass": "B",
        "ISO3166-2": "GB",
        "Country": "GB",
        "ISO3166-3": "GBR",
        "Locality": "Aberdeen",
        "MatchRuleLabel": "Rlfnp",
        "PostalCode": "AB11 6PH",
        "PostalCodePrimary": "AB11 6PH",
        "Thoroughfare": "Exchange Street"
    }]
}]

@patch('loqate_international_batch_cleanse.api.RequestHandler.call_geocoding_api', Mock(return_value=happy_response))
def test_address_geocode_check_happy(client):
    body = {
        "credentials": {
            "apikey": "Test",
        },
        "input_data": {
            "address": {
                "type": "STRUCTURED",
                "country": "GBR",
            }
        }
    }

    expected_metadata = {
        "geocode_accuracy": {
            "status": "AVERAGE",
            "level": "THOROUGHFARE",
        }
    }
    expected_address = {
        "country": "GBR",
        "latitude": 57.145618,
        "longitude": -2.096897,
        "route": "Exchange Street",
        "postal_code": "AB11 6PH",
        "locality": "Aberdeen",
        "premise": "Imperial House 12-14",
        "type": "STRUCTURED",
    }

    response = client.post("/check", json=body)
    json_response = response.json

    assert json_response['output_data']['metadata'] == expected_metadata
    assert json_response['output_data']['address'] == expected_address

@patch('loqate_international_batch_cleanse.api.RequestHandler.call_geocoding_api', Mock(return_value=no_geocode_response))
def test_address_geocode_check_faild(client):
    body = {
        "credentials": {
            "apikey": "Test",
        },
        "input_data": {
            "address": {
                "type": "STRUCTURED",
                "country": "GBR",
            }
        }
    }

    expected_metadata = {
        "geocode_accuracy": {
            "status": "FAILED",
        }
    }

    expected_address = {
        "country": "GBR",
        "route": "Exchange Street",
        "postal_code": "AB11 6PH",
        "locality": "Aberdeen",
        "premise": "Imperial House 12-14",
        "type": "STRUCTURED",
    }

    response = client.post("/check", json=body)
    json_response = response.json


    assert json_response['output_data']['metadata'] == expected_metadata
    assert json_response['output_data']['address'] == expected_address
