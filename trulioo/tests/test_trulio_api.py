import pytest 
import json
from unittest.mock import Mock, patch
from collections import namedtuple

from trulioo.api import validate_authentication
from trulioo.api import consents
from trulioo.api import verify

Response = namedtuple('Response', ['status_code', 'json'])

@patch('trulioo.api.requests.get', Mock(return_value=Response(200, lambda: 'Ok')))
def test_authentication(client):
    user = 'dummy_user'
    password = 'dummy_pass'
    assert validate_authentication(user, password) == 200


@patch('api.views.validate_authentication')
def test_health_check(mock_authentication, client):

    mock_authentication.return_value=200

    response = client.post(
        '/health-check',
        data=json.dumps({
            'credentials' :{
                'username': 'dummy_user',
                'password': 'dummy_pass'}}),
        content_type='application/json'
    )

    mock_authentication.assert_called_with('dummy_user', 'dummy_pass')
    assert response.status_code == 200


@patch('trulioo.api.requests.get', Mock(return_value=Response(200, lambda: [])))
def test_empty_list_of_consents(client):
    user = 'dummy_user'
    password = 'dummy_pass'
    response = consents(user, password, 'GB')
    assert response == []


@patch('trulioo.api.requests.get', Mock(return_value=Response(200, lambda: ["Birth Registry",
                                                                            "Visa Verification",
                                                                            "DVS ImmiCard Search",
                                                                            "DVS Citizenship Certificate Search",
                                                                            "Credit Agency"])))
def test_empty_list_of_consents(client):
    user = 'dummy_user'
    password = 'dummy_pass'
    response = consents(user, password, 'GB')
    assert response == ["Birth Registry",
                        "Visa Verification",
                        "DVS ImmiCard Search",
                        "DVS Citizenship Certificate Search",
                        "Credit Agency"]


@patch('trulioo.api.requests.post')
@patch('trulioo.api.consents', Mock(return_value=["Birth Registry"]))
def test_verify_request(mock_post_verify, client):
    user = 'dummy_user'
    password = 'dummy_pass'
    verify(user, password, 'GB', {"PersonInfo":{"FirstGivenName":"Julia"}})

    headers = {'Content-Type': 'application/json'}
    url = 'https://api.globaldatacompany.com/verifications/v1/verify'

    base_body = {
        "AcceptTruliooTermsAndConditions": True, 
        "CleansedAddress": False, 
        "ConfigurationName": "Identity Verification", 
        "CountryCode": 'GB',
        "DataFields": {"PersonInfo":{"FirstGivenName":"Julia"}}, 
        "VerboseMode": False,
        "ConsentForDataSources": ["Birth Registry"]
    }

    mock_post_verify.assert_called_with(
        url, 
        auth=(user, password), 
        data=json.dumps(base_body), 
        headers=headers)





