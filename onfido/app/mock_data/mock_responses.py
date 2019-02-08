mock_uk_response = {
    'errors': [],
    'output_data': {
        'credit_ref': {
            'dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'exact': {
                'v': {
                    'count': 3,
                    'match': True
                }
            },
            'partial': {
                'v': {
                    'count': 3,
                    'match': True
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'telephone_partial': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_uk_response_one_plus_one = {
    'errors': [],
    'output_data': {
        'credit_ref': {
            'dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_uk_response_fail = {
    'errors': [],
    'output_data': {
        'credit_ref': {
            'dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_two_plus_two = {
    'errors': [],
    'output_data': {
        '_cls': 'python.models.entities.IndividualData.IndividualData',
        'credit_ref': {
            'exact': {
                'v': {
                    'count': 3,
                    'match': True
                }
            },
            'dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'consumer_dob': {
                                'properties': {},
                                'result': 'clear'
                            },

                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_one_plus_one = {
    'errors': [],
    'output_data': {
        '_cls': 'python.models.entities.IndividualData.IndividualData',
        'credit_ref': {
            'exact': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'government_exact': {
                'v': {
                    'count': 1,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_fail = {
    'errors': [],
    'output_data': {
        '_cls': 'python.models.entities.IndividualData.IndividualData',
        'credit_ref': {
            'exact': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'dob': {
                'v': {
                    'count': 0,
                    'match': True
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 0,
                    'match': True
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'created_at': '2018-02-21T15:39:46Z',
            'download_uri': 'https://onfido.com/dashboard/pdf/information_requests/8916590',
            'form_uri': None,
            'href': '/v2/applicants/ef72bcbc-08b1-40bc-aa83-ac4c80d5aa72/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'id': '277756dd-84d0-4c08-96fe-c8d9391b74d4',
            'paused': False,
            'redirect_uri': None,
            'report_type_groups': ['3766'],
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {
                                    'number_of_credit_agencies': '3'
                                },
                                'result': 'clear'
                            },
                            'telephone_database': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'unidentified'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'credit_agencies': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'voting_register': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'mortality': {
                        'result': 'clear'
                    }
                },
                'created_at': '2018-02-21T15:39:46Z',
                'href': '/v2/checks/277756dd-84d0-4c08-96fe-c8d9391b74d4/reports/9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'id': '9e2e1bda-1b9a-48e9-87dd-c23d079c948a',
                'name': 'identity',
                'properties': {},
                'result': 'clear',
                'status': 'complete',
                'sub_result': None,
                'variant': 'kyc'
            }],
            'result': 'clear',
            'results_uri': 'https://onfido.com/dashboard/information_requests/8916590',
            'sandbox': True,
            'status': 'complete',
            'tags': [],
            'type': 'express',
            'version': '2.0'
        }
    }
}

mock_usa_response = {
    'errors': [],
    'output_data': {
        'credit_ref': {
            'exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'partial': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            }
        },
        'db_matches': {
            'business_registration_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'business_registration_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'commercial_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'consumer_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'electoral_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'government_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'onfido_proprietary_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'postal_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'ssn_exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'ssn_partial': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'telephone_exact': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'telephone_partial': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'telephone_dob': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_dob': {
                'v': {
                    'count': 1,
                    'match': True
                }
            },
            'utility_partial': {
                'v': {
                    'count': 0,
                    'match': False
                }
            },
            'utility_exact': {
                'v': {
                    'count': 0,
                    'match': False
                }
            }
        }
    },
    'price': 0,
    'raw': {
        'applicant': {
            'id': 'some_id'
        },
        'check': {
            'reports': [{
                'breakdown': {
                    'address': {
                        'breakdown': {
                            'address_matched': {
                                'properties': {
                                    'sources': 'Credit Agencies, Telephone Database'
                                },
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'date_of_birth': {
                        'breakdown': {
                            'date_of_birth_matched': {
                                'properties': {
                                    'sources': 'Credit Agencies, Utility Registration'
                                },
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    },
                    'properties': {},
                    'ssn': {
                        'breakdown': {
                            'full_match': {
                                'properties': {},
                                'result': 'clear'
                            },
                            'last_4_digits_match': {
                                'properties': {},
                                'result': 'clear'
                            }
                        },
                        'result': 'clear'
                    }
                },
                'created_at': '2014-05-23T13:50:33Z',
                'href': '/v2/checks/8546922-234234-234234/reports/6951786-234234-316712',
                'id': '6951786-234234-316712',
                'name': 'identity',
                'result': 'clear',
                'status': 'complete'
            }]
        }
    }
}

mock_watchlist_consider = {
    'error': [],
    'output_data': {
        'sanctions_results': [{
            'match_id': 'f584b7e5-ce09-4474-8365-a024eef576fb',
            'locations': [{
                'v': {
                    'country': 'GBR'
                }
            }],
            'remarks': [{
                'v': 'Leader of party'
            }],
            'match_name': {
                'v': 'Demo watchlist'
            },
            'sanctions': [{
                    'v': {
                        'name': 'Sanction sanction',
                        'issuer': 'WorldBank',
                        'is_current': True
                    }
                },
                {
                    'v': {
                        'name': 'Sanctioned',
                        'is_current': True
                    }
                }
            ],
            'gender': {
                'v': 'Male'
            },
            'pep': {
                'v': {
                    'match': True,
                    'tier': 1,
                    'roles': [{
                        'name': 'Head of state',
                        'tier': 1
                    }, {
                        'name': 'Family member',
                        'tier': 2
                    }]
                }
            },
            'aliases': [{
                'v': 'Watchlist Test'
            }, {
                'v': 'Tested Listed'
            }],
            'sources': [{
                    'v': {
                        'name': '',
                        'url': 'http://www.google.com'
                    }
                },
                {
                    'v': {
                        'name': '',
                        'url': 'http://www.yahoo.com'
                    }
                }
            ],
            'media': [{
                    'v': {
                        'url': 'http://www.bbc.com',
                        'title': 'A Headline'
                    }
                },
                {
                    'v': {
                        'url': 'http://www.news.com',
                        'title': 'Another headline'
                    }
                }
            ]
        }]
    },
    'raw': {}
}

mock_watchlist_pass = {
    'error': [],
    'output_data': {
        'sanctions_results': []
    },
    'raw': {}
}