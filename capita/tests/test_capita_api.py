import os
import pytest 
import json
from unittest.mock import Mock, patch
from collections import namedtuple

from capita.api import echo_test_request, verify

Response = namedtuple('Response', ['status_code', 'json'])

@patch('capita.api.requests.get', Mock(return_value=Response(200, lambda: 'API Running')))
def test_authentication(client):
    credentials = {
        'license_key': 'dummy-license-key',
        'client_key': 'dummy_key',
        'profile_short_code': 'eKYC',
        'url': 'dummy_url'}
    assert echo_test_request(credentials) == 200


@patch('api.views.echo_test_request')
def test_ealth_check(mock_authentication, client):

    mock_authentication.return_value = 200

    credentials = {
        'credentials':{
            'license_key': 'dummy-license-key',
            'client_key': 'dummy_key',
            'profile_short_code': 'eKYC',
            'url': 'dummy_url'}}

    response = client.post(
        '/health',
        data=json.dumps(credentials),
        content_type='application/json'
    )

    mock_authentication.assert_called_with(credentials['credentials'])
    assert response.status_code == 200

def test_health_check_empty(client):
    response = client.post(
        '/health',
        data=json.dumps({}),
        content_type='application/json'
    )

    assert response.status_code == 200

def test_health_check_get_method(client):
    response = client.get('/health')
    assert response.status_code == 200


@patch('capita.api.requests.post')
def test_verify_request(mock_post_verify, client):
    mock_post_verify.return_value = Response(200, lambda: {'test': 'ok'})

    credentials = {
        'license_key': 'dummy-license-key',
        'client_key': 'dummy_key',
        'profile_short_code': 'eKYC',
        'url': 'dummy_url'}

    dummy_body = {'pkg': 'test'}
    
    request_proxy = os.getenv('REQUEST_PROXY')
    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + f"?profileShortCode={credentials['profile_short_code']}"
    
    auth = (credentials['license_key'], credentials['client_key'])
    verify(dummy_body, credentials)

    mock_post_verify.assert_called_with(
        url=url,
        headers=headers,
        auth=auth,
        data=json.dumps(dummy_body))




