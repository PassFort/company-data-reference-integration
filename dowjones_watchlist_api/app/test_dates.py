import unittest

import xmltojson

from app.api.dowjones_types import (
    Date,
)
from app.api.types import (
    DateMatchData,
    FullName,
    PersonalDetails,
)


class TestSerializeDateMatch(unittest.TestCase):
    def test_does_nothing_to_partial_date(self):
        match = DateMatchData({
            'type': 'DOB',
            'date': '1954',
        })
        self.assertEqual('1954', match.to_primitive()['date'])


class TestDateFromDowJonesConversion(unittest.TestCase):
    def test_captures_all_fields_from_full_date(self):
        date_xml = '<date day="28" month="4" year="1937" date-type="Date of Birth"></date>'
        dowjones_date = Date()
        dowjones_date.import_data(xmltojson.parse(date_xml))
        self.assertEqual(dowjones_date.to_partial_date_string(), '1937-04-28')

    def test_captures_only_year_and_month_if_no_day(self):
        date_xml = '<date month="4" year="1937" date-type="Date of Birth"></date>'
        dowjones_date = Date()
        dowjones_date.import_data(xmltojson.parse(date_xml))
        self.assertEqual(dowjones_date.to_partial_date_string(), '1937-04')

    def test_captures_only_year_if_no_month_or_day(self):
        date_xml = '<date year="1937" date-type="Date of Birth"></date>'
        dowjones_date = Date()
        dowjones_date.import_data(xmltojson.parse(date_xml))
        self.assertEqual(dowjones_date.to_partial_date_string(), '1937')


class TestPartialDateToDowJonesConversion(unittest.TestCase):
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
