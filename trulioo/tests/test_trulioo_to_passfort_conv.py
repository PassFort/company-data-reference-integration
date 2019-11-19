import pytest

from trulioo.convert_data import trulioo_to_passfort_data


def test_empty_package(client):
    response_body = trulioo_to_passfort_data({}, {})

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
        },
        "raw": {},
        "errors": []
    }


def test_record_with_empty_datasource_results(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_without_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstInitial',
                            'Status': 'nomatch'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": "Credit Agency",
                        "database_type": "CREDIT",
                        "matched_fields": []
                    },
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_surname_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['SURNAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_forename_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstGivenName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['FORENAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_dob_complete_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'DayOfBirth',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'MonthOfBirth',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['DOB'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_dob_year_month_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'MonthOfBirth',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['DOB'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_dob_year_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'YearOfBirth',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['DOB'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_dob_day_nomatch(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'DayOfBirth',
                            'Status': 'nomatch'
                        },
                        {
                            'FieldName': 'MonthOfBirth',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'YearOfBirth',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": "Credit Agency",
                        "database_type": "CREDIT",
                        "matched_fields": []
                    },
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_partial_address_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'StreetName',
                            'Status': 'match'
                        },
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({
        'Location': {
            'BuildingNumber': '10',
            'StreetName': 'Wellbeing street',
            'PostalCode': 'PPC CCC',
        },
    }, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            "entity_type": "INDIVIDUAL",
            "electronic_id_check": {
                "matches": [
                    {
                        "database_name": "Credit Agency",
                        "database_type": "CREDIT",
                        "matched_fields": []
                    },
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_address_match(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'BuildingNumber',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StreetName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'PostalCode',
                            'Status': 'match'
                        },
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({
        'Location': {
            'BuildingNumber': '10',
            'StreetName': 'Wellbeing street',
            'PostalCode': 'PPC CCC',
        },
    }, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['ADDRESS'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_address_match_full_fields(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'BuildingNumber',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'UnitNumber',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StreetName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'City',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'Suburb',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'County',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StateProvinceCode',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'PostalCode',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({
        'Location': {
            'BuildingNumber': '10',
            'BuildingName': 'My building',
            'UnitNumber': '248',
            'StreetName': 'Mandoline street',
            'City': 'Aloco',
            'Suburb': 'Deuce',
            'County': 'Alibobo',
            'StateProvinceCode': 'ZZZ',
            'PostalCode': 'EPP MMM',
        }
    }, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['ADDRESS'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_address_nomatch_by_partial_fields(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstGivenName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingNumber',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'BuildingName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'UnitNumber',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StreetName',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'City',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'Suburb',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'County',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'StateProvinceCode',
                            'Status': 'match'
                        },
                        {
                            'FieldName': 'PostalCode',
                            'Status': 'nomatch'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['FORENAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_database_type_credit(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['SURNAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_one_datasource_with_database_type_civil(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Electoral Roll',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Electoral Roll',
                        'database_type': 'CIVIL',
                        'matched_fields': ['SURNAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_two_datasource_with_diff_database_type(client):
    trulioo_data = {
        'Record': {
            'DatasourceResults': [
                {
                    'DatasourceName': 'Credit Agency',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
                {
                    'DatasourceName': 'Electoral Roll',
                    'DatasourceFields': [
                        {
                            'FieldName': 'FirstSurName',
                            'Status': 'match'
                        }
                    ],
                    'Errors': [],
                    'FieldGroups': []
                },
            ],
            'Errors': []
        },
        'Errors': []
    }

    response_body = trulioo_to_passfort_data({}, trulioo_data)

    assert response_body == {
        "decision": "FAIL",
        "output_data": {
            'entity_type': 'INDIVIDUAL',
            'electronic_id_check': {
                'matches': [
                    {
                        'database_name': 'Credit Agency',
                        'database_type': 'CREDIT',
                        'matched_fields': ['SURNAME'],
                        'count': 1,
                    },
                    {
                        'database_name': 'Electoral Roll',
                        'database_type': 'CIVIL',
                        'matched_fields': ['SURNAME'],
                        'count': 1,
                    }
                ]
            }
        },
        "raw": trulioo_data,
        "errors": []
    }


def test_record_with_national_id_match(client):
    for id_field_name in [
        'nationalid',
        'health',
        'socialservice',
        'taxidnumber',
    ]:
        trulioo_data = {
            'Record': {
                'DatasourceResults': [
                    {
                        'DatasourceName': 'National id database',
                        'DatasourceFields': [
                            {
                                'FieldName': 'FirstSurName',
                                'Status': 'match'
                            },
                            {
                                'FieldName': id_field_name,
                                'Status': 'match'
                            }
                        ],
                        'Errors': [],
                        'FieldGroups': []
                    },
                ],
                'Errors': []
            },
            'Errors': []
        }

        response_body = trulioo_to_passfort_data({}, trulioo_data)

        assert response_body == {
            "decision": "FAIL",
            "output_data": {
                'entity_type': 'INDIVIDUAL',
                'electronic_id_check': {
                    'matches': [
                        {
                            'database_name': 'National id database',
                            'database_type': 'CIVIL',
                            'matched_fields': ['SURNAME', 'IDENTITY_NUMBER'],
                            'count': 1,
                        },
                    ]
                }
            },
            "raw": trulioo_data,
            "errors": []
        }


def test_record_error_missing_required_fields_generic(client):
    trulioo_data = {'Errors': [
        {'Code': '1001', 'Message': 'Missing required field: unsupported field name'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 101,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': [{'Code': '1001', 'Message': 'Missing required field: unsupported field name'}],
            }),
            'message': 'Missing required fields',
        }]
    }

    assert 'timestamp' in response_body['errors'][0]['info']


def test_record_error_missing_required_fields_1001(client):
    trulioo_data = {'Errors': [
        {'Code': '1001', 'Message': 'Missing required field: BuildingName'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 101,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': [{'Code': '1001', 'Message': 'Missing required field: BuildingName'}],
                'missing_fields': [
                    '/address_history/0/premise',
                ],
            }),
            'message': 'Missing required fields',
        }]
    }


def test_record_error_missing_required_fields_4001(client):
    trulioo_data = {'Errors': [
        {'Code': '4001', 'Message': 'Missing required field: BuildingName'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 101,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': [{'Code': '4001', 'Message': 'Missing required field: BuildingName'}],
                'missing_fields': [
                    '/address_history/0/premise',
                ],
            }),
            'message': 'Missing required fields',
        }]
    }


def test_record_error_missing_required_fields_3005(client):
    trulioo_data = {'Errors': [
        {'Code': '3005', 'Message': 'Missing required field: BuildingName'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 101,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': [{'Code': '3005', 'Message': 'Missing required field: BuildingName'}],
                'missing_fields': [
                    '/address_history/0/premise',
                ],
            }),
            'message': 'Missing required fields',
        }]
    }


def test_record_error_missing_required_fields_concatened(client):
    trulioo_data = {'Errors': [{'Code': '1001'},
                               {'Code': '4001'}, {'Code': '3005'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 101,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': [{'Code': '1001'}, {'Code': '4001'}, {'Code': '3005'}],
            }),
            'message': 'Missing required fields',
        }]
    }


def test_record_error_unknown_error(client):
    trulioo_data = {'Errors': [{'Code': '2000'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 303,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': {
                    'Code': '2000',
                },
            }),
            'message': "Provider Error: Unknown error while running 'Trulioo' service",
        }],
    }


def test_record_error_invalid_input_data_1006(client):
    trulioo_data = {'Errors': [{'Code': '1006'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 201,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': {
                    'Code': '1006',
                },
            }),
            'message': 'The submitted data was invalid. Provider returned error code 1006'
        }]
    }


def test_record_error_invalid_input_data_1008(client):
    trulioo_data = {'Errors': [{'Code': '1008'}]}
    response_body = trulioo_to_passfort_data({}, trulioo_data)
    assert response_body == {
        "decision": "ERROR",
        "output_data": {},
        "raw": trulioo_data,
        "errors": [{
            'source': 'PROVIDER',
            'code': 201,
            'info': PartialComparator({
                'provider': 'Trulioo',
                'original_error': {
                    'Code': '1008',
                },
            }),
            'message': 'The submitted data was invalid. Provider returned error code 1008'
        }]
    }


class PartialComparator:
    def __init__(self, partial_dict={}):
        self.partial_dict = partial_dict

    def __repr__(self):
        return f'({self.__name__}) {repr(self.partial_dict)}'

    def __eq__(self, other):
        if type(other) is not dict:
            return False
        return self.partial_dict.items() <= other.items()
