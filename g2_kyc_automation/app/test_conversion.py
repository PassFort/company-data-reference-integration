from unittest import TestCase
from app.types import CompanyData, G2Report, G2CompassResult, StructuredAddress
from schematics.exceptions import DataError


g2_report_data = {
    "pdf_url": "https://kyc-files.s3.amazonaws.com/scan_pdfs/httpwwwexamplecom_2020-02-11_22-40-58-UTC_seACGC.pdf",
    "messages": {
        "warn": [
            "The following required pages could not be found: Payment Policy",
            "The following required pages could not be found: Refund Policy",
        ],
        "ok": [
            "Prohibited phrases were not found.",
            "Alexa reported no adult content."
        ],
        "crit": [
            "YellowPages.com requires a business address.",
            "OpenCorporates corporate search not run. No business address was provided."
        ],
        "info": [
            "This is a high traffic site (Alexa rank 26037)"
        ]
    },
    "g2_compass_results": [{
        "compass_score": "1",
        "reason_codes": [
            {
                "code": "105200",
                "description": "Whois record is private"
            },
            {
                "code": "105470",
                "description": "Monitored without incident for more than 3 years, last monitored between 4 and 12 months ago"
            }
        ],
        "valid_url": "true",
        "fraudfile_matches": [],
        "search_term": {
            "merchant_name": "Blade HQ",
            "merchant_url": "http://www.bladehq.com"
        },
        "site_active": "null",
        "request_id": "197cb011-ec13-4295-a6a2-d5a44b9cc087",
        "status": "complete"
    }],
    "malware_detections": {"phishings": 0, "malwares": 0}
}

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


class TestFromPassfortToG2(TestCase):
    def test_address_validation(self):
        address = {
            "country": "GBR",
            "locality": "LONDON"
        }

        with self.assertRaises(DataError):
            address = StructuredAddress().import_data(address)
            address.validate()

    def test_minimal_input(self):
        data: CompanyData = CompanyData().import_data(input_data, apply_defaults=True)
        data.validate()

        expected = {
            "company_name": "Passfort",
            "url": "https://www.passfort.com",
            "business_address": {
                "country": "GB",
                "city": "London",
                "state": "England"
            },
            "vendor_id": "79E25148-BB64-4280-962C-738436151487"
        }

        self.assertEqual(expected, data.as_request())


class TestFromG2ToPassfort(TestCase):
    def test_parses_report_data(self):
        report: G2Report = G2Report().import_data(g2_report_data, apply_defaults=True)
        report.validate()

        expected = {
            "g2_compass_score": {
                "score": 1,
                "reason_codes": [
                    {"name": "105200", "value": "Whois record is private"},
                    {"name": "105470", "value": "Monitored without incident for more than 3 years, last monitored between 4 and 12 months ago"}
                ],
                "request_id": "197cb011-ec13-4295-a6a2-d5a44b9cc087",
            },
            "pdf_url": "https://kyc-files.s3.amazonaws.com/scan_pdfs/httpwwwexamplecom_2020-02-11_22-40-58-UTC_seACGC.pdf",
            "assessment_messages": [
                {"level": "CRITICAL", "description": "YellowPages.com requires a business address."},
                {"level": "CRITICAL", "description": "OpenCorporates corporate search not run. No business address was provided."},
                {"level": "WARNING", "description": "The following required pages could not be found: Payment Policy"},
                {"level": "WARNING", "description": "The following required pages could not be found: Refund Policy"},
                {"level": "INFO", "description": "This is a high traffic site (Alexa rank 26037)"},
                {"level": "OK", "description": "Prohibited phrases were not found."},
                {"level": "OK", "description": "Alexa reported no adult content."},
            ],
            "valid_url": True,
            "is_active": None,
            "provider_id": "1234",
        }

        self.assertEqual(expected, report.to_passfort("1234"))
