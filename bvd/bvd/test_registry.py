import json
from unittest import TestCase

from bvd.registry import format_company_type, format_structured_company_type

class TestFormatRawData(TestCase):

    def test_format_company_type(self):
        raw_data = get_raw_data()
        self.assertEqual(format_company_type(raw_data), 'Public limited companies')

    def test_format_structured_company_type(self):
        raw_data = get_raw_data()
        structured_company_type = format_structured_company_type(raw_data)
        self.assertEqual(structured_company_type.is_public, True)
        self.assertEqual(structured_company_type.is_limited, True)


def get_raw_data():
    with open("./demo_data/registry/GBR_GB01493087_01493087.json", 'rb') as f:
        return json.loads(f.read())['raw']
