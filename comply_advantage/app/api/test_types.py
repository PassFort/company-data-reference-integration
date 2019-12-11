import unittest

from .types import PersonalDetails
from ..file_utils import get_response_from_file


def sample_profile_dob(dob):
    return PersonalDetails({'name': {'given_names': ['Test'], 'family_name': 'User'}, 'dob': dob})


class TestConvertPersonalDetails(unittest.TestCase):

    def test_interprets_full_dob_correctly(self):
        profile = sample_profile_dob('1969-07-20')
        self.assertEqual(profile.year_from_dob(), 1969)

    def test_interprets_partial_year_month_dob_correctly(self):
        profile = sample_profile_dob('1969-07')
        self.assertEqual(profile.year_from_dob(), 1969)

    def test_interprets_partial_year_dob_correctly(self):
        profile = sample_profile_dob('1969')
        self.assertEqual(profile.year_from_dob(), 1969)

    def test_interprets_parses_invalid_dates_as_none(self):
        profile = sample_profile_dob('xyzzy')
        self.assertIsNone(profile.year_from_dob())