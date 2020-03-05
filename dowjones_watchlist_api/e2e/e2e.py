import requests
import unittest

API_URL = 'http://localhost:8001'


class TestApiValidation(unittest.TestCase):

    def test_health_check_passes(self):
        response = requests.get(
            f'{API_URL}/health',
        )
        self.assertEqual(response.status_code, 200)
