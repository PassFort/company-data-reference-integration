import json
import pytest
from unittest.mock import Mock, patch

TRULIOO_RESPONSE_DATA = {
    'TransactionID': 'eeaf7fd3-a35d-4df2-ae4c-adaec46630a0',
    'UploadedDt': '2019-06-19T20:49:13',
    'CountryCode': 'GB',
    'ProductName': 'Identity Verification',
    'Record': {
        'TransactionRecordID': '1ea59f23-6d9d-4559-8c9a-b1c145674ce8',
        'RecordStatus': 'nomatch',
        'DatasourceResults': [
            {
                'DatasourceName': 'Credit Agency',
                'DatasourceFields': [
                    {
                        'FieldName': 'MonthOfBirth',
                        'Status': 'nomatch'
                    }, {
                        'FieldName': 'FirstInitial',
                        'Status': 'nomatch'
                    }
                ],
                'Errors': [],
                'FieldGroups': []
            },
            {
                'DatasourceName': 'Credit Agency 3',
                'DatasourceFields': [
                    {
                        'FieldName': 'FirstGivenName',
                        'Status': 'nomatch'
                    }
                ],
                'AppendedFields': [],
                'Errors': [],
                'FieldGroups': []
            }
        ],
        'Errors': [],
        'Rule': {
            'RuleName': 'RuleScript NameAddressDoB',
            'Note': 'Script manually created'
        }
    },
    'Errors': []
}


@patch('api.views.passfort_to_trulioo_data', Mock(return_value=({}, 'GB', {})))
@patch('api.views.verify', Mock(return_value={'Record': {'DatasourceResults': []}}))
def test_ekyc_check(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass'}}),
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
        "decision": "ERROR",
        "output_data": {
        },
        "raw": {},
        "errors": [{'code': 201, 'message': 'The submitted data was invalid'}]
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
        "decision": "ERROR",
        "output_data": {
        },
        "raw": {},
        "errors": [{'code': 203, 'message': 'Missing provider credentials'}]
    }


def test_ekyc_check_wrong_method(client):
    response = client.get('/ekyc-check')
    assert response.status_code == 405
    assert response.headers['Content-Type'] == 'application/json'


@patch('api.views.passfort_to_trulioo_data', Mock(return_value=({}, 'GB', {})))
@patch('api.views.verify', Mock(return_value=TRULIOO_RESPONSE_DATA))
def test_ekyc_check_with_raw_data(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass'}}),
        content_type='application/json'
    )
    assert response.status_code == 200
    assert response.headers['Content-Type'] == 'application/json'
    assert response.json == {
        "decision": "FAIL",
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "provider_reference_number": "eeaf7fd3-a35d-4df2-ae4c-adaec46630a0",
                "matches": [
                    {
                        "database_name": "Credit Agency",
                        "database_type": "CREDIT",
                        "matched_fields": []
                    },
                    {
                        "database_name": "Credit Agency 3",
                        "database_type": "CREDIT",
                        "matched_fields": []
                    }
                ]
            }
        },
        "raw": TRULIOO_RESPONSE_DATA,
        "errors": []
    }


def test_ekyc_check_demo_fail_data(client):
    response = client.post(
        '/ekyc-check',
        data=json.dumps({
            'credentials': {
                'username': 'dummy_user',
                'password': 'dummy_pass'
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
        "decision": "FAIL",
        "output_data": {
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
                'password': 'dummy_pass'
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
        "decision": "PASS",
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "provider_reference_number": "demo_provider_reference",
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
