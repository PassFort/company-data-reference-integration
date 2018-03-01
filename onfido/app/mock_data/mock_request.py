mock_request = {'config': {},
 'credentials': {'_cls': 'passfort_data_structure.stage_config.onfido.OnfidoCredentialsNoToken', 'token': 'test_bQqXUdkaKMHJczn9wxYcg6FiZoyiK8_A'},
 'input_data': {'_cls': 'python.models.entities.IndividualData.IndividualData',
                'address_history': {'all_': [[{'administrative_area_level_1': 'TX',
                                               'country': 'USA',
                                               'formatted_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                               'locality': 'Springfield',
                                               'original_address': ', 21, Fake '
                                                                   'street, '
                                                                   'Springfield, '
                                                                   'Springfield, '
                                                                   'TX, 42223',
                                               'original_structured_address': {'country': 'USA',
                                                                               'locality': 'Springfield',
                                                                               'postal_code': '42223',
                                                                               'postal_town': 'Springfield',
                                                                               'route': 'Fake '
                                                                                        'street',
                                                                               'state_province': 'TX',
                                                                               'street_number': '21',
                                                                               'subpremise': ''},
                                               'postal_code': '42223',
                                               'postal_town': 'Springfield',
                                               'route': 'Fake street',
                                               'street_number': '21',
                                               'subpremise': ''},
                                              {}]],
                                    'current': {'administrative_area_level_1': 'TX',
                                                'country': 'USA',
                                                'formatted_address': ', 21, '
                                                                     'Fake '
                                                                     'street, '
                                                                     'Springfield, '
                                                                     'Springfield, '
                                                                     'TX, '
                                                                     '42223',
                                                'locality': 'Springfield',
                                                'original_address': ', 21, '
                                                                    'Fake '
                                                                    'street, '
                                                                    'Springfield, '
                                                                    'Springfield, '
                                                                    'TX, 42223',
                                                'original_structured_address': {'country': 'USA',
                                                                                'locality': 'Springfield',
                                                                                'postal_code': '42223',
                                                                                'postal_town': 'Springfield',
                                                                                'route': 'Fake '
                                                                                         'street',
                                                                                'state_province': 'TX',
                                                                                'street_number': '21',
                                                                                'subpremise': ''},
                                                'postal_code': '42223',
                                                'postal_town': 'Springfield',
                                                'route': 'Fake street',
                                                'street_number': '21',
                                                'subpremise': ''}},
                'personal_details': {'dob': {'v': '1993-01-01'},
                                     'name': {'v': {'family_name': 'AMERICAN',
                                                    'given_names': ['AMERICAAN']}}}},
 'is_demo': False}


mock_fail_applicant_response = {'error': {'fields': {'dob': ['must be before 2018-02-25 00:00:00']},
                                          'message': 'There was a validation error on this request',
                                          'type': 'validation_error'}}