import json
import pytest
from unittest.mock import Mock, patch

LEXISNEXIS_RESPONSE_DATA = {'status': 200, 'body': {'InstantIDResponseEx': {'response': {'Result': {}}}}}


@patch('api.views.passfort_to_lexisnexis_data', Mock(return_value=({})))
@patch('api.views.verify', Mock(return_value=LEXISNEXIS_RESPONSE_DATA))
def test_ekyc_check(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass',
                'url': 'dummy_url'}}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'


def test_ekyc_check_empty_package(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == {
        "output_data": {
        },
        "raw": {},
        "errors": [{'code': 201, 'message': 'INVALID_INPUT_DATA'}]
    }


def test_ekyc_check_api_key_empty(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({'credentials': ''}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == {
        "output_data": {
        },
        "raw": {},
        "errors": [{'code': 203, 'message': 'MISSING_API_KEY'}]
    }


def test_ekyc_check_wrong_method(client):
    response = client.get('/ekyc-check')
    assert response.status_code == 405
    assert response.headers['Content-Type'] == 'application/json'


@patch('api.views.passfort_to_lexisnexis_data', Mock(return_value=({})))
@patch('api.views.verify', Mock(return_value=LEXISNEXIS_RESPONSE_DATA))
def test_ekyc_check_with_raw_data(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass',
                'url': 'dummy_url'}}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == {
        "output_data": {
            "decision": "FAIL",
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [],
            }
        },
        "raw": LEXISNEXIS_RESPONSE_DATA['body'],
        "errors": []
    }


def test_ekyc_check_demo_fail_data(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass',
                'url': 'dummy_url'
            },
            'input_data': {
                'personal_details': {
                    'name': {
                        'given_names': ['Todd', 'Fail']
                    }
                }
            },
            'is_demo': True
        }),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [],
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }


def test_ekyc_check_demo_1_valid_data(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass',
                'url': 'dummy_url'
            },
            'input_data': {
                'personal_details': {
                    'name': {
                        'given_names': ['Todd', '1+1']
                    }
                }
            },
            'is_demo': True
        }),
        content_type='application/json'
    )

    matched_fields = [
        "FORENAME",
        "SURNAME",
        "ADDRESS",
        "DOB"
    ]
    demo_response = {
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": 'Credit Agency',
                        "database_type": 'CREDIT',
                        "matched_fields": matched_fields,
                        "count": 1
                    }
                ]
            }
        },
        "raw": "Demo response, Generated Automatically",
        "errors": []
    }

    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == demo_response
