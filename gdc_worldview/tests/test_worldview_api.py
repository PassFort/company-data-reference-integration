import os
import pytest 
import json
from unittest.mock import Mock, patch
from collections import namedtuple

from worldview.api import echo_test_request, verify

Response = namedtuple('Response', ['status_code', 'json'])

@patch('worldview.api.requests.post', Mock(return_value=Response(200, lambda: 'API Running')))
def test_authentication(client):
    credentials = {
        "username": "dummy-user",
        "password": "dummy-pass",
        "tenant": "dummy-tenant",
        "url": "https://api.globaldataconsortium.com/rest/validate"
    }
    assert echo_test_request(credentials) == 200


@patch('api.views.echo_test_request')
def test_health_check(mock_authentication, client):

    mock_authentication.return_value = 200

    credentials = {
        'credentials':{
            "username": "dummy-user",
            "password": "dummy-pass",
            "tenant": "dummy-tenant",
            "url": "https://api.globaldataconsortium.com/rest/validate"
        }
    }

    response = client.post(
        '/health-check',
        data=json.dumps(credentials),
        content_type='application/json'
    )

    mock_authentication.assert_called_with(credentials['credentials'])
    assert response.status_code == 200

def test_health_check_empty(client):
    response = client.post(
        '/health-check',
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code == 200

def test_health_check_get_method(client):
    response = client.get('/health-check')
    assert response.status_code == 200


@patch('worldview.api.requests.post')
def test_verify_request(mock_post_verify, client):
    mock_post_verify.return_value = Response(200, lambda: {'test': 'ok'})

    credentials = {
        "username": "dummy-user",
        "password": "dummy-pass",
        "tenant": "dummy-tenant",
        "url": "https://api.globaldataconsortium.com/rest/validate"
    }

    dummy_body = {'pkg': 'test'}
    
    headers = {'Content-Type': 'application/json'}
    
    auth = (credentials['username'], credentials['password'])
    verify(dummy_body, credentials)

    mock_post_verify.assert_called_with(
        url=credentials['url'],
        headers=headers,
        data='{"pkg": "test", "credentials": {"username": "dummy-user", "password": "dummy-pass", "tenant": "dummy-tenant"}}')



