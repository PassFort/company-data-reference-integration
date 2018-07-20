import json
from unittest import TestCase
from unittest.mock import patch

from bvd.registry import StructuredCompanyType, OwnershipType, format_company_type, format_structured_company_type

class TestFormatRawData(TestCase):

    def test_format_company_type(self):
        raw_data = get_raw_data()
        self.assertEqual(format_company_type(raw_data), 'Public limited companies')

    def test_format_structured_company_type(self):
        raw_data = get_raw_data()
        structured_company_type = format_structured_company_type(raw_data)
        self.assertEqual(structured_company_type.is_public, True)
        self.assertEqual(structured_company_type.is_limited, True)
        self.assertEqual(structured_company_type.ownership_type, OwnershipType.COMPANY)

    @patch('bvd.registry.send_sentry_exception')
    def test_cannot_structure_unrecognised_company_type(self, send_sentry_exception):
        raw_data = get_unrecognised_company_type_raw_data()
        structured_company_type = format_structured_company_type(raw_data)
        send_sentry_exception.assert_called_once()
        self.assertEqual(hasattr(structured_company_type, 'is_public'), False)
        self.assertEqual(hasattr(structured_company_type, 'is_limited'), False)
        self.assertEqual(hasattr(structured_company_type, 'ownership_type'), False)


def get_raw_data():
    with open("./demo_data/registry/GBR_GB01493087_01493087.json", 'rb') as f:
        return json.loads(f.read())['raw']

def get_unrecognised_company_type_raw_data():
    with open("./demo_data/registry/unrecognised_company_type.json", 'rb') as f:
        return json.loads(f.read())['raw']
