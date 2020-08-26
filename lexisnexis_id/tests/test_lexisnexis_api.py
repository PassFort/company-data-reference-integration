import os
import pytest
import json
from unittest.mock import Mock, patch
from collections import namedtuple

from lexisnexis.api import echo_test_request, verify

Response = namedtuple('Response', ['status_code', 'json'])


@patch('lexisnexis.api.requests.post', Mock(return_value=Response(200, lambda: 'Ok')))
def test_authentication(client):
    credentials = {
        'username': 'dummy_user',
        'password': 'dummy_pass',
        'url': 'dummy_url'}
    assert echo_test_request(credentials) == 200


@patch('api.views.echo_test_request')
def test_health_check(mock_authentication, client):
    mock_authentication.return_value = 200

    credentials = {
        'credentials': {
            'username': 'dummy_user',
            'password': 'dummy_pass',
            'url': 'dummy_endpoint'}}

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


@patch('lexisnexis.api.requests.post')
def test_verify_request(mock_post_verify, client):
    mock_post_verify.return_value = Response(200, lambda: {'test': 'ok'})

    credentials = {
        'username': 'dummy_user',
        'password': 'dummy_pass',
        'url': 'dummy_endpoint'}
    dummy_body = {'pkg': 'test'}

    headers = {'Content-Type': 'application/json'}
    url = credentials['url'] + "/WsIdentity/InstantID?ver_=2.6"

    auth = (credentials['username'], credentials['password'])
    verify(dummy_body, credentials)

    mock_post_verify.assert_called_with(
        url=url,
        headers=headers,
        auth=auth,
        data=json.dumps(dummy_body))
