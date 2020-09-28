import unittest
import requests

API_URL = "http://localhost:8001"
COMPANY_DATA_URL = API_URL + "/company-data-check"


class EndToEndTests(unittest.TestCase):
    def test_health_endpoint(self):
        response = requests.get(API_URL + "/health")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), "success")

    def test_demo_company_data(self):
        response = requests.post(
            COMPANY_DATA_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"country_of_incorporation": "GBR", "bvd_id": "pass",},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["metadata"]["name"], "PASSFORT LIMITED"
        )
        self.assertEqual(response.json()["output_data"]["metadata"]["bvd_id"], "pass")
