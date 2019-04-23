successful_work_request = {
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

successful_study_request = {
    'config': {'visa_check_type': 'STUDY'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '77777777',
            'country_code': 'IND'
        }],
        'personal_details': {
            'dob': '1999-01-01',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}


unidentified_person_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '12121212',
            'country_code': 'BMU'
        }],
        'personal_details': {
            'dob': '2000-11-11',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}

no_visa_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '37373737',
            'country_code': 'FIN'
        }],
        'personal_details': {
            'dob': '2000-12-12',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}

login_error_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '37373737',
            'country_code': 'GAB'
        }],
        'personal_details': {
            'dob': '2000-07-07',
            'name': {
                'family_name': 'Smith',
                'given_names': ['John']
            }
        }
    },
    'is_demo': False
}
