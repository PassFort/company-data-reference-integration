from unittest import TestCase
from .utils import normalize_params


class TestAuth(TestCase):

    def test_normalize_params(self):
        url = "https://sandbox.api.mastercard.com?Page=0&Length=1"
        params = {
            "secret": "thing",
            "auth": "1.0"
        }
        expected = "Length=1&Page=0&auth=1.0&secret=thing"
        actual = normalize_params(url, params)

        self.assertEqual(expected, actual)
