import unittest

from app.api.types import (
    PersonalDetails,
    FullName
)

class TestPartialDateConversion(unittest.TestCase):
    def test_does_nothing_to_full_dob(self):
        details = PersonalDetails({
            'name': FullName({
                'given_names': ['David'],
                'family_name': 'Cameron',
            }),
            'dob': '1966-10-9'
        })
        self.assertEqual(details.dowjones_dob, '1966-10-9')

    def test_appends_wildcard_to_year_month(self):
        details = PersonalDetails({
            'name': FullName({
                'given_names': ['David'],
                'family_name': 'Cameron',
            }),
            'dob': '1966-10'
        })
        self.assertEqual(details.dowjones_dob, '1966-10-A')

        
    def test_appends_wildcard_to_year(self):
        details = PersonalDetails({
            'name': FullName({
                'given_names': ['David'],
                'family_name': 'Cameron',
            }),
            'dob': '1966'
        })
        self.assertEqual(details.dowjones_dob, '1966-A-A')
