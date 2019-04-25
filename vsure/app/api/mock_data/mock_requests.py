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
    'is_demo': True
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
    'is_demo': True
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
                'given_names': ['NOT_FOUND']
            }
        }
    },
    'is_demo': True
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
                'given_names': ['NO_VISA']
            }
        }
    },
    'is_demo': True
}

expired_request = {
    'config': {'visa_check_type': 'STUDY'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '467567r67',
            'country_code': 'FRA'
        }],
        'personal_details': {
            'dob': '2000-12-12',
            'name': {
                'family_name': 'Smith',
                'given_names': ['EXPIRED']
            }
        }
    },
    'is_demo': True
}

no_expiry_request = {
    'config': {'visa_check_type': 'WORK'},
    'credentials': {'api_key': 'JtGXbnOxncr1MZZ'},
    'input_data': {
        'documents_metadata': [{
            'document_type': 'PASSPORT',
            'number': '1237687263',
            'country_code': 'IND'
        }],
        'personal_details': {
            'dob': '2000-12-12',
            'name': {
                'family_name': 'Smith',
                'given_names': ['NO_EXPIRY']
            }
        }
    },
    'is_demo': True
}
