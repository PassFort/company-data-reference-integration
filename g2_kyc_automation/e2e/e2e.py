import unittest
import requests

API_URL = 'http://localhost:8001'

input_data = {
    "metadata": {
        "name": "Passfort",
        "contact_details": {
            "url": "https://www.passfort.com"
        },
        "addresses": [{
            "address": {
                "country": "GBR",
                "locality": "London",
                "state_province": "England"
            }
        }]
    },
    "customer_ref": "79E25148-BB64-4280-962C-738436151487",
}

config = {
    "config": {
        "use_sandbox": True
    },
    "credentials": {
        "client_id": "garbage",
        "client_secret": "garbage"
    },
    "is_demo": True,
}

create_payload = {
    **config,
    "input_data": input_data,
}

case_payload = {
    **config,
    "input_data": {
        "case_id": "pass"
    }
}


class EndToEndTests(unittest.TestCase):
    def test_health_endpoint(self):
        response = requests.get(API_URL + '/health')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), 'success')

    def test_create_report(self):
        response = requests.post(API_URL + '/screening_request', json=create_payload)
        json = response.json()
        self.assertEqual(response.status_code, 200)
        self.assertEqual(json['output_data']['case_id'], 'pass')

    def test_poll_report(self):
        response = requests.post(API_URL + '/poll_report', json=case_payload)
        self.assertEqual(response.status_code, 200)

    def test_retrieve_report(self):
        response = requests.post(API_URL + '/report', json=case_payload)
        json = response.json()
        self.assertEqual(response.status_code, 200)
        expected = {
            "g2_compass_score": {
                "score": 1,
                "reason_codes": [
                    {
                        "name": "105150",
                        "value": "URL previously associated with high-risk MCC"
                    }
                ],
                "request_id": "633c15a2-78e7-4b8a-917c-b81c58e1a1ae"
            },
            "assessment_messages": [
                {
                    "level": "INFO",
                    "description": "This is a high traffic site (Alexa rank 13983)"
                },
                { "level": "OK", "description": "Prohibited phrases were not found." },
                {
                    "level": "OK",
                    "description": "No Consumer Financial Protection Bureau results Consumer Complaints Database results were found."
                },
                {
                    "level": "OK",
                    "description": "Google SafeBrowsing reported no malware or phishing."
                },
                {
                    "level": "OK",
                    "description": "No search results found on the Federal Trade Commission web site."
                },
                { "level": "OK", "description": "No Justia lawsuits found." },
                { "level": "OK", "description": "Alexa reported no adult content." }
            ],
            "pdf_url": "https://kyc-files.s3.amazonaws.com/scan_pdfs/httpwwwexamplecom_2020-02-11_22-40-58-UTC_seACGC.pdf",
            "valid_url": True,
            "is_active": None,
            "provider_id": "pass",

        }
        self.assertEqual(json['output_data'], expected)

