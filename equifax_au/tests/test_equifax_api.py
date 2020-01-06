import pytest 
import json
from unittest.mock import Mock, patch
from collections import namedtuple

from equifax.api import echo_test_request, verify

Response = namedtuple('Response', ['status_code', 'text'])

@patch('equifax.api.requests.post', Mock(return_value=Response(200, '<soapenv:Envelope><soapenv:Body><test></test></soapenv:Body></soapenv:Envelope>')))
def test_authentication(client):
    request_data = {
        'username': 'dummy_user',
        'password': 'dummy_pass',
        'url': 'dummy_endpoint'}
    assert echo_test_request(request_data) == ('Equifax Integration', 200,)


@patch('api.views.echo_test_request')
def test_health_check(mock_authentication, client):

    mock_authentication.return_value = ("Equifax Integration", 200,)

    response = client.post(
        '/health',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass',
                'url': 'dummy_endpoint'}
            }
        ),
        content_type='application/json'
    )

    assert response.status_code == 200

    mock_authentication.assert_called_with({
            'username': 'dummy_user',
            'password': 'dummy_pass',
            'url': 'dummy_endpoint'})
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


@patch('equifax.api.requests.post')
def test_verify_request(mock_post_verify, client):
    url = 'dummy_endpoint'
    dummy_body = '<xml><header></header></xml>'
    headers = {'Content-Type': 'text/xml; charset=utf-8'}
    url = 'xyz'

    verify(dummy_body, url)

    mock_post_verify.assert_called_with(
        url+'/sys2/idmatrix-v4',  
        data=dummy_body, 
        headers=headers)
