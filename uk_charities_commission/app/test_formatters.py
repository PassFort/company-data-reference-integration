import unittest
import os
import requests
from schemad_types.utils import get_in

from flask import json
from app.formatters import format_trustee, format_charity
from dassert import Assert


class TestFormatTrustees(unittest.TestCase):
    def test_it_formats_individual_trustees(self):
        result = format_trustee({'TrusteeName': 'Mr Henry Irish'})
        Assert.equal(result['immediate_data']['personal_details']['name']['given_names'], ['Henry'])
        Assert.equal(result['immediate_data']['personal_details']['name']['family_name'], 'Irish')

    def test_it_formats_individual_trustees_with_multiple_forenames(self):
        result = format_trustee({'TrusteeName': 'Mr Henry Bob Irish'})
        Assert.equal(result['immediate_data']['personal_details']['name']['given_names'], ['Henry', 'Bob'])
        Assert.equal(result['immediate_data']['personal_details']['name']['family_name'], 'Irish')

    def test_all_test_data(self):
        raw_file_names = [f for f in os.listdir('test_data') if f.startswith('RAW_')]

        for raw_file_name in raw_file_names:
            formatted_file_name = raw_file_name.replace('RAW_', 'FORMATTED_')

            with open(f'test_data/{raw_file_name}', 'r') as raw_file:
                raw_data = json.loads(raw_file.read())
                formatted_data = format_charity(raw_data)

            with open(f'test_data/{formatted_file_name}', 'r') as formatted_file:
                expected_formatted_data = json.loads(formatted_file.read())

            self.assertEqual(formatted_data, expected_formatted_data)
