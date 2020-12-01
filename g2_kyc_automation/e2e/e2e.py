import unittest
import requests

API_URL = 'http://localhost:8001'

class EndToEndTests(unittest.TestCase):
    def test_health_endpoint(self):
        response = requests.get(API_URL + '/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'success')
