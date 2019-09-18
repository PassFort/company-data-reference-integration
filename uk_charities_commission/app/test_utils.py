from unittest import TestCase

from app.utils import permissive_string_compare


class TestStringCompare(TestCase):

    def test_it_handles_casing(self):
        self.assertTrue(permissive_string_compare('HELLO', 'Hello'))

    def test_it_handles_spacing(self):
        self.assertTrue(permissive_string_compare('hello world', 'hello world'))
        self.assertTrue(permissive_string_compare('hello world', 'hello\tworld'))

    def test_it_handles_special_characters(self):
        self.assertTrue(permissive_string_compare('hello\'s', 'hellos'))
        self.assertTrue(permissive_string_compare('h.ello.', 'hello'))

    def test_it_handles_hard_combinations(self):
        self.assertTrue(permissive_string_compare('^HELLo $ world\'s', 'hello worlds'))

    def test_it_handles_shortened_company_numbers(self):
        self.assertTrue(permissive_string_compare('012345678', '12345678'))
