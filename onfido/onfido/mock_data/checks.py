mock_uk_check = {'data': {
    'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
    'created_at': '2018-02-21T15:39:46Z',
    'status': 'complete',
    'redirect_uri': None,
    'type': 'express',
    'result': 'clear',
    'sandbox': True,
    'report_type_groups': [
        '3766'
    ],
    'tags': [

    ],
    'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
    'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
    'form_uri': None,
    'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
    'reports': [
        {
            'created_at': '2018-02-21T15:39:46Z',
            'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
            'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
            'name': 'identity',
            'properties': {

            },
            'result': 'clear',
            'status': 'complete',
            'sub_result': None,
            'variant': 'kyc',
            'breakdown': {
                'mortality': {
                    'result': 'clear'
                },
                'date_of_birth': {
                    'result': 'clear',
                    'breakdown': {
                        'credit_agencies': {
                            'result': 'clear',
                            'properties': {

                            }
                        },
                        'voting_register': {
                            'result': 'clear',
                            'properties': {

                            }
                        }
                    }
                },
                'address': {
                    'result': 'clear',
                    'breakdown': {
                        'credit_agencies': {
                            'result': 'clear',
                            'properties': {
                                'number_of_credit_agencies': '3'
                            }
                        },
                        'voting_register': {
                            'result': 'unidentified',
                            'properties': {

                            }
                        },
                        'telephone_database': {
                            'result': 'clear',
                            'properties': {

                            }
                        }
                    }
                }
            }
        }
    ],
    'paused': False,
    'version': '2.0'
},
    'expected_database_matches': {'business_registration_dob': {'v': {'count': 0, 'match': False}},
                                  'business_registration_exact': {'v': {'count': 0, 'match': False}},
                                  'business_registration_partial': {'v': {'count': 0, 'match': False}},
                                  'commercial_dob': {'v': {'count': 0, 'match': False}},
                                  'commercial_exact': {'v': {'count': 0, 'match': False}},
                                  'commercial_partial': {'v': {'count': 0, 'match': False}},
                                  'consumer_dob': {'v': {'count': 0, 'match': False}},
                                  'consumer_exact': {'v': {'count': 0, 'match': False}},
                                  'consumer_partial': {'v': {'count': 0, 'match': False}},
                                  'electoral_exact': {'v': {'count': 0, 'match': False}},
                                  'electoral_partial': {'v': {'count': 0, 'match': False}},
                                  'electoral_dob': {'v': {'count': 1, 'match': True}},
                                  'government_exact': {'v': {'count': 0, 'match': False}},
                                  'government_partial': {'v': {'count': 0, 'match': False}},
                                  'government_dob': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_dob': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_exact': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_partial': {'v': {'count': 0, 'match': False}},
                                  'postal_dob': {'v': {'count': 0, 'match': False}},
                                  'postal_exact': {'v': {'count': 0, 'match': False}},
                                  'postal_partial': {'v': {'count': 0, 'match': False}},
                                  'telephone_exact': {'v': {'count': 1, 'match': True}},
                                  'telephone_partial': {'v': {'count': 1, 'match': True}},
                                  'telephone_dob': {'v': {'count': 0, 'match': False}},
                                  'utility_dob': {'v': {'count': 0, 'match': False}},
                                  'utility_exact': {'v': {'count': 0, 'match': False}},
                                  'utility_partial': {'v': {'count': 0, 'match': False}}},
    'expected_source_count': {'is_alive': True, 'address': {'business_registration': {'count': 0},
                                                            'commercial_database': {'count': 0},
                                                            'consumer_database': {'count': 0},
                                                            'credit_agencies': {'count': '3'},
                                                            'government': {'count': 0},
                                                            'postal_authorities': {'count': 0},
                                                            'proprietary': {'count': 0},
                                                            'telephone_database': {'count': 1},
                                                            'utility_registration': {'count': 0},
                                                            'voting_register': {'count': 0}},
                              'dob': {'business_registration': {'count': 0},
                                      'commercial_database': {'count': 0},
                                      'consumer_database': {'count': 0},
                                      'credit_agencies': {'count': 1},
                                      'government': {'count': 0},
                                      'postal_authorities': {'count': 0},
                                      'proprietary': {'count': 0},
                                      'telephone_database': {'count': 0},
                                      'utility_registration': {'count': 0},
                                      'voting_register': {'count': 1}}
                              },
    'expected_credit_ref': {'exact': {'v': {'count': 3, 'match': True}},
                            'partial': {'v': {'count': 3, 'match': True}},
                            'dob': {'v': {'count': 1, 'match': True}}}
}

mock_usa_check = {'data': {'reports': [{
    "id": "6951786-234234-316712",
    "name": "identity",
    "created_at": "2014-05-23T13:50:33Z",
    "status": "complete",
    "result": "clear",
    "href": "/v2/checks/8546922-234234-234234/reports/6951786-234234-316712",
    "breakdown": {
        "date_of_birth": {
            "result": "clear",
            "breakdown": {
                "date_of_birth_matched": {
                    "result": "clear",
                    "properties": {
                        "sources": "Credit Agencies, Utility Registration"
                    }
                }
            }
        },
        "address": {
            "result": "clear",
            "breakdown": {
                "address_matched": {
                    "result": "clear",
                    "properties": {
                        "sources": "Credit Agencies, Telephone Database"
                    }
                }
            }
        },
        "ssn": {
            "result": "clear",
            "breakdown": {
                "last_4_digits_match": {
                    "result": "clear",
                    "properties": {}
                },
                "full_match": {
                    "result": "clear",
                    "properties": {}
                }
            }
        },
        "properties": {}
    }
}]},
    'expected_database_matches': {'business_registration_dob': {'v': {'count': 0,
                                                                      'match': False}},
                                  'business_registration_exact': {'v': {'count': 0,
                                                                        'match': False}},
                                  'business_registration_partial': {'v': {'count': 0,
                                                                          'match': False}},
                                  'commercial_dob': {'v': {'count': 0, 'match': False}},
                                  'commercial_exact': {'v': {'count': 0, 'match': False}},
                                  'commercial_partial': {'v': {'count': 0, 'match': False}},
                                  'consumer_dob': {'v': {'count': 0, 'match': False}},
                                  'consumer_exact': {'v': {'count': 0, 'match': False}},
                                  'consumer_partial': {'v': {'count': 0, 'match': False}},
                                  'electoral_dob': {'v': {'count': 0, 'match': False}},
                                  'electoral_exact': {'v': {'count': 0, 'match': False}},
                                  'electoral_partial': {'v': {'count': 0, 'match': False}},
                                  'government_dob': {'v': {'count': 0, 'match': False}},
                                  'government_exact': {'v': {'count': 0, 'match': False}},
                                  'government_partial': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_dob': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_exact': {'v': {'count': 0, 'match': False}},
                                  'onfido_proprietary_partial': {'v': {'count': 0,
                                                                       'match': False}},
                                  'postal_dob': {'v': {'count': 0, 'match': False}},
                                  'postal_exact': {'v': {'count': 0, 'match': False}},
                                  'postal_partial': {'v': {'count': 0, 'match': False}},
                                  'ssn_exact': {'v': {'count': 1, 'match': True}},
                                  'ssn_partial': {'v': {'count': 1, 'match': True}},
                                  'telephone_dob': {'v': {'count': 0, 'match': False}},
                                  'telephone_exact': {'v': {'count': 1, 'match': True}},
                                  'telephone_partial': {'v': {'count': 1, 'match': True}},
                                  'utility_dob': {'v': {'count': 1, 'match': True}},
                                  'utility_exact': {'v': {'count': 0, 'match': False}},
                                  'utility_partial': {'v': {'count': 0, 'match': False}}},
    'expected_credit_ref': {'dob': {'v': {'count': 1, 'match': True}},
                            'exact': {'v': {'count': 1, 'match': True}},
                            'partial': {'v': {'count': 1, 'match': True}}},
    'expected_source_count': {'is_alive': None, 'address': {
        'ssn': {'count': 1},
        'business_registration': {'count': 0},
        'commercial_database': {'count': 0},
        'consumer_database': {'count': 0},
        'credit_agencies': {'count': 1},
        'government': {'count': 0},
        'postal_authorities': {'count': 0},
        'proprietary': {'count': 0},
        'telephone_database': {'count': 1},
        'utility_registration': {'count': 0},
        'voting_register': {'count': 0}},
                              'dob': {'business_registration': {'count': 0},
                                      'commercial_database': {'count': 0},
                                      'consumer_database': {'count': 0},
                                      'credit_agencies': {'count': 1},
                                      'government': {'count': 0},
                                      'postal_authorities': {'count': 0},
                                      'proprietary': {'count': 0},
                                      'telephone_database': {'count': 0},
                                      'utility_registration': {'count': 1},
                                      'voting_register': {'count': 0}}},
}

mock_usa_ssn_fail_check = {'data': {'reports': [{
    "id": "6951786-234234-316712",
    "name": "identity",
    "created_at": "2014-05-23T13:50:33Z",
    "status": "complete",
    "result": "clear",
    "href": "/v2/checks/8546922-234234-234234/reports/6951786-234234-316712",
    "breakdown": {
        "date_of_birth": {
            "result": "clear",
            "breakdown": {
                "date_of_birth_matched": {
                    "result": "clear",
                    "properties": {
                        "sources": "Utility Registration, Business Registration"
                    }
                }
            }
        },
        "address": {
            "result": "clear",
            "breakdown": {
                "address_matched": {
                    "result": "clear",
                    "properties": {
                        "sources": "Credit Agencies, Telephone Database"
                    }
                }
            }
        },
        "ssn": {
            "result": "unidentified",
            "breakdown": {
                "last_4_digits_match": {
                    "result": "unidentified",
                    "properties": {}
                },
                "full_match": {
                    "result": "unidentified",
                    "properties": {}
                }
            }
        },
        "properties": {}
    }
}]},
    'expected_source_count': {'is_alive': None, 'address': {
        'ssn': {'count': 0},
        'business_registration': {'count': 0},
        'commercial_database': {'count': 0},
        'consumer_database': {'count': 0},
        'credit_agencies': {'count': 1},
        'government': {'count': 0},
        'postal_authorities': {'count': 0},
        'proprietary': {'count': 0},
        'telephone_database': {'count': 1},
        'utility_registration': {'count': 0},
        'voting_register': {'count': 0}},
                              'dob': {'business_registration': {'count': 1},
                                      'commercial_database': {'count': 0},
                                      'consumer_database': {'count': 0},
                                      'credit_agencies': {'count': 0},
                                      'government': {'count': 0},
                                      'postal_authorities': {'count': 0},
                                      'proprietary': {'count': 0},
                                      'telephone_database': {'count': 0},
                                      'utility_registration': {'count': 1},
                                      'voting_register': {'count': 0}}},
}
