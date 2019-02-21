mock_uk_matches = [
    {
        'count': 1,
        'database_name': 'Onfido (credit source #1)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Onfido (credit source #2)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Onfido (credit source #3)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Telephone Database',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Onfido (credit source #1)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'DOB']
    },
    {
        'count': 1,
        'database_name': 'Voting Register',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'DOB']
    }
]

mock_uk_matches_one_plus_one = [
    {
        'count': 1,
        'database_name': 'Onfido (credit source #1)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 0,
        'database_name': 'Telephone Database',
        'database_type': 'CIVIL',
        'matched_fields': []
    },
    {
        'count': 0,
        'database_name': 'Voting Register',
        'database_type': 'CIVIL',
        'matched_fields': []
    }
]

mock_uk_matches_fail = [
    {
        'count': 0,
        'database_name': 'Onfido (all credit sources)',
        'database_type': 'CREDIT',
        'matched_fields': []
    },
    {
        'count': 0,
        'database_name': 'Telephone Database',
        'database_type': 'CIVIL',
        'matched_fields': []
    },
    {
        'count': 0,
        'database_name': 'Voting Register',
        'database_type': 'CIVIL',
        'matched_fields': []
    }
]

mock_usa_matches = [
    {
        'count': 1,
        'database_name': 'Onfido (credit source #1)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Telephone Database',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'ADDRESS']
    },
    {
        'count': 1,
        'database_name': 'Onfido (credit source #1)',
        'database_type': 'CREDIT',
        'matched_fields': ['FORENAME', 'SURNAME', 'DOB']
    },
    {
        'count': 1,
        'database_name': 'Utility Registration',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'DOB']
    },
    {
        'count': 1,
        'database_name': 'Social Security Database',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'IDENTITY_NUMBER_SUFFIX']
    },
    {
        'count': 1,
        'database_name': 'Social Security Database',
        'database_type': 'CIVIL',
        'matched_fields': ['FORENAME', 'SURNAME', 'IDENTITY_NUMBER']
    },
    {
        'count': 0,
        'database_name': 'Voting Register',
        'database_type': 'CIVIL',
        'matched_fields': []
    },
    {
        'count': 0,
        'database_name': 'Government',
        'database_type': 'CIVIL',
        'matched_fields': []
    }
]

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