import unittest
from app.api.passfort_convert import find_exact_matching_associate, check_field, find_fuzzy_matching_associate


class TestPassfortToMatch(unittest.TestCase):
    def test_find_fuzzy_match_associate(self):
        input = [
            {
                "FirstName": "Davi",
                "LastName": "Smith",
            },
            {
                "FirstName": "Davi",
                "LastName": "Smit",
            }
        ]

        output = {
            "FirstName": "David",
            "LastName": "Smith",
        }

        matches = [("Name", "M02")]

        found_idx = find_fuzzy_matching_associate(input, matches, output)

        self.assertEqual(found_idx, 0)

    def test_check_field(self):
        input = {
            "FirstName": "David",
            "LastName": "Smith",
            "Address": {
                "Line1": "23 Dovecote",
                "Country": "GBR",
                "City": "London"
            },
            "PhoneNumber": "12345678"
        }

        output = {
            "FirstName": "David",
            "LastName": "Smith",
            "Address": {
                "Line1": "23 Dovecote",
                "Country": "GBR",
                "City": "London"
            },
            "PhoneNumber": "12345678"
        }

        fields = ['Name', 'Address', 'PhoneNumber']
        (self.assertTrue(check_field(input, output, f)) for f in fields)

        with self.subTest("ignores optional fields in compound match"):
            input = {
                "Address": {
                    "Line1": "23 Dovecote",
                    "Country": "USA",
                    "City": "New York"
                }
            }

            output = {
                "Address": {
                    "Line1": "23 Dovecote",
                    "Country": "USA",
                    "City": "New York",
                    "PostalCode": "12345",
                }
            }

            self.assertTrue(check_field(input, output, "Address"))
