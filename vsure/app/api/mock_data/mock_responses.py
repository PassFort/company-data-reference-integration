no_visa_response = {
    'failure_reason': 'Error: Does not hold a valid visa',
    'visas': []
}

login_error_response = {
    'errors': [{
        'code': 303,
        'info': {'raw': 'Error: VEVO login error'},
        'message': 'Error: VEVO login error',
        'source': 'PROVIDER'
    }]
}

successful_work_response = {
    'failure_reason': None,
    'visas': [{
        'country_code': 'AUS',
        'details': [
            {'name': 'Work Entitlement Description', 'value': 'The visa holder has unlimited right to work in Australia.'},
            {'name': 'Visa Applicant', 'value': 'Primary'},
            {'name': 'Visa Class', 'value': 'SI'},
            {'name': 'Visa Type', 'value': '820'},
            {'name': 'Visa Type Details', 'value': 'For partners of Australian citizens and permanent residents'}
        ],
        'entitlement': 'WORK',
        'expiry_date': '2030-10-22',
        'grant_date': '2000-03-14',
        'holder': {
            'dob': '2000-01-01',
            'document_checked': {
                'country_code': 'IND',
                'document_type': 'PASSPORT',
                'number': '77777777'
            },
            'full_name': 'John Smith'
        },
        'name': 'Partner'
    }]
}

successful_study_response = {
    'failure_reason': None,
    'visas': [{
        'country_code': 'AUS',
        'details': [
            {"name": "Study Condition", "value": "No limitations on study."},
            {"name": "Visa Applicant", "value": "Primary"},
            {"name": "Visa Class", "value": "SI"},
            {"name": "Visa Type", "value": "457"},
            {"name": "Visa Type Details", "value": "For people sponsored by an employer previously named Business (Long Stay)"},
        ],
        'entitlement': 'STUDY',
        'expiry_date': '2030-10-22',
        'grant_date': '2000-10-22',
        'holder': {
            'dob': '1999-01-01',
            'document_checked': {
                'country_code': 'IND',
                'document_type': 'PASSPORT',
                'number': '77777777'
            },
            'full_name': 'John Smith'
        },
        'name': 'Temporary Work (Skilled)'
    }]
}


expired_response = {
    'failure_reason': None,
    'visas': [{
        'country_code': 'AUS',
        'details': [
            {'name': 'Study Condition', 'value': 'No limitations on study.'},
            {'name': 'Visa Applicant', 'value': 'Primary'},
            {'name': 'Visa Class', 'value': 'SI'},
            {'name': 'Visa Type', 'value': '457'},
            {'name': 'Visa Type Details', 'value': 'For people sponsored by an employer previously named Business (Long Stay)'}
        ],
        'entitlement': 'STUDY',
        'expiry_date': '2010-10-22',
        'grant_date': '2000-10-22',
        'holder': {
            'dob': '2000-12-12',
            'document_checked': {
                'country_code': 'FRA',
                'document_type': 'PASSPORT',
                'number': '467567r67'
            },
            'full_name': 'EXPIRED Smith'
        },
        'name': 'Temporary Work (Skilled)'
    }]
}

no_expiry_response = {
    'failure_reason': None,
    'visas': [{
        'country_code': 'AUS',
        'details': [
            {'name': 'Work Entitlement Description', 'value': 'The visa holder has unlimited right to work in Australia.'},
            {'name': 'Visa Applicant', 'value': 'Primary'},
            {'name': 'Visa Class', 'value': 'SI'},
            {'name': 'Visa Type', 'value': '820'},
            {'name': 'Visa Type Details', 'value': 'For partners of Australian citizens and permanent residents'}
        ],
        'entitlement': 'WORK',
        'expiry_date': None,
        'grant_date': '2000-03-14',
        'holder': {
            'dob': '2000-12-12',
            'document_checked': {
                'country_code': 'IND',
                'document_type': 'PASSPORT',
                'number': '1237687263'
            },
            'full_name': 'NO_EXPIRY Smith'
        },
        'name': 'Partner'
    }]
}

unidentified_person_response = {
    'failure_reason': 'Could not complete visa check - The Department has not been able to identify the person. Please check that the details you entered in are correct.',
    'visas': []
}
