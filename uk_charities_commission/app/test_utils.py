from unittest import TestCase

from app.utils import string_compare


class TestStringCompare(TestCase):

    def test_it_handles_casing(self):
        self.assertTrue(string_compare('HELLO', 'Hello'))

    def test_it_handles_spacing(self):
        self.assertTrue(string_compare('hello world', 'hello world'))
        self.assertTrue(string_compare('hello world', 'hello\tworld'))

    def test_it_handles_special_characters(self):
        self.assertTrue(string_compare('hello\'s', 'hellos'))
        self.assertTrue(string_compare('h.ello.', 'hello'))

    def test_it_handles_hard_combinations(self):
        self.assertTrue(string_compare('^HELLo $ world\'s', 'hello worlds'))
