import unittest
import requests

API_URL = "http://localhost:8001"
COMPANY_DATA_URL = API_URL + "/company-data-check"
CREATE_PORTFOLIO_URL = API_URL + "/monitoring_portfolio"
ADD_TO_PORTFOLIO_URL = API_URL + "/monitoring"


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
                "input_data": {"country_of_incorporation": "GBR", "bvd_id": "pass"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["metadata"]["name"], "PASSFORT LIMITED"
        )
        self.assertEqual(response.json()["output_data"]["metadata"]["bvd_id"], "pass")

    def test_create_monitoring_portfolio(self):
        response = requests.post(
            CREATE_PORTFOLIO_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"name": "d1c3f995-e502-457d-9f58-7bc75a242769"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["id"], "4ed92e40-a501-eb11-90b5-d89d672fa480"
        )

    def test_add_to_monitoring_portfolio(self):
        response = requests.post(
            ADD_TO_PORTFOLIO_URL,
            json={
                "is_demo": True,
                "credentials": {"key": "NOT_USED_BY_DEMO"},
                "input_data": {"portfolio_id": "4ed92e40-a501-eb11-90b5-d89d672fa480", "bvd_id": "pass"},
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.json()["errors"])
        self.assertEqual(
            response.json()["output_data"]["id"], "4ed92e40-a501-eb11-90b5-d89d672fa480"
        )
