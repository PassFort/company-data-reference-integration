mock_successful_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '77777777',
            'country_code': 'IND'
        }],
        'personal_details': {
            'dob': '2000-01-01',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}


mock_unidentified_person_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '97979797',
            'country_code': 'Gabon'
        }],
        'personal_details': {
            'dob': '2000-08-07',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}
