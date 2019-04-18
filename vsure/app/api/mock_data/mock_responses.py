unidentified_person_response = {
    'errors': [{
        'code': 303,
        'info': {'raw': 'Error: VEVO cannot identify the person'},
        'message': 'Error: VEVO cannot identify the person',
        'source': 'PROVIDER'
    }]
}

no_visa_response = {
    "failure_reason": "Error: Does not hold a valid visa",
    "visas": [{
        "details": [{
            "name": "Visa Type",
            "value": '0'
        }],
        'dob': '2000-12-12',
        'entitlement': 'WORK',
        'expiry_date': None,
        'full_name': 'John Novisa',
        'grant_date': None,
        'name': None,
        'document_checked': {
            'document_type': 'PASSPORT',
            'country_code': 'FIN',
            'number': '37373737',
        }
    }]
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
    "failure_reason": "",
    "visas": [{
        "details": [
            {'name': 'Work Entitlement Description', 'value':'The visa holder has unlimited right to work in Australia.'},
            {'name': 'Visa Applicant', 'value':'Primary'},
            {'name': 'Visa Class','value':'SI'},
            {'name': 'Visa Type','value':'820'},
            {'name': 'Visa Type Details','value':'For partners of Australian citizens and permanent residents'}
        ],
        'dob': '2000-01-01',
        'document_checked': {
            'country_code': 'IND',
            'document_type': 'PASSPORT',
            'number': '22222222',
        },
        'entitlement': 'WORK',
        'expiry_date': None,
        'full_name': 'John Smith',
        'grant_date': '2014-03-14',
        'name': 'Partner'
    }]
}

successful_study_response = {
    "failure_reason": "",
    "visas": [{
        "details": [
            {"name": "Study Condition", "value": "No limitations on study."},
            {"name": "Visa Applicant", "value": "Primary"},
            {"name": "Visa Class", "value": "SI"},
            {"name": "Visa Type", "value": "457"},
            {"name": "Visa Type Details", "value": "For people sponsored by an employer previously named Business (Long Stay)"},
        ],
        'dob': '1999-01-01',
        'document_checked': {
           'country_code': 'IND',
           'document_type': 'PASSPORT',
           'number': '77777777'
        },
        'entitlement': 'STUDY',
        'expiry_date': '2019-10-22',
        'full_name': 'Student Visa',
        'grant_date': '2015-10-22',
        'name': 'Temporary Work (Skilled)'
    }]
}
