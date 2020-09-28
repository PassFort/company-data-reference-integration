import json
from mock import patch
from unittest import TestCase

from app.bvd.types import(
    RegistryData,
    RegistryResult,
)
from app.passfort.types import (
    CompanyMetadata,
    ContactDetails,
    IndustryClassification,
    IndustryClassificationType,
    PreviousName,
    TaxId,
    TaxIdType,
)
from app.passfort.structured_company_type import OwnershipType


class TestMetadata(TestCase):
    def test_registry_check(self):
        with open("./demo_data/registry/pass.json") as demo_file:
            bvd_result = RegistryResult(json.load(demo_file))
            bvd_result.validate()

            metadata = CompanyMetadata.from_bvd(bvd_result.data[0])
            metadata.validate()

            self.assertEqual(metadata.bvd_id, "pass")
            self.assertEqual(metadata.number, "09565115")
            self.assertEqual(metadata.bvd9, "230418860")
            self.assertIsNone(metadata.isin)
            self.assertIsNone(metadata.lei)
            # TODO: Should we accept n.a. for Tax IDs?
            self.assertEqual(
                metadata.tax_ids,
                [TaxId({
                    "tax_id_type": TaxIdType.EUROVAT.value,
                    "value": "n.a."
                })]
            )
            self.assertEqual(
                metadata.name,
                "PASSFORT LIMITED"
            )
            self.assertEqual(
                metadata.contact_information.url,
                "www.passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.email,
                "info@passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.phone_number,
                "+44 20 3633 1761",
            )
            self.assertEqual(
                metadata.freeform_address,
                "MEZZANINE FLOOR 24 CORNHILL, EC3V 3ND, LONDON, United Kingdom"
            )
            self.assertTrue(metadata.is_active)
            self.assertEqual(metadata.is_active_details, "Active")
            self.assertEqual(metadata.trade_description, "Business and domestic software development")
            self.assertIsNone(metadata.description)


class TestCompanyType(TestCase):
    def test_company_type(self):
        bvd_data = RegistryData({
            "STANDARDISED_LEGAL_FORM": "Private limited companies"
        })
        metadata = CompanyMetadata.from_bvd(bvd_data)
        self.assertEqual(metadata.company_type, "Private limited companies")

    def test_known_structured_company_type(self):
        bvd_data = RegistryData({
            "STANDARDISED_LEGAL_FORM": "Private limited companies"
        })
        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertFalse(metadata.structured_company_type.is_public)
        self.assertTrue(metadata.structured_company_type.is_limited)
        self.assertEqual(metadata.structured_company_type.ownership_type, OwnershipType.COMPANY.value)

    @patch('app.passfort.structured_company_type.logging')
    def test_unknown_structured_company_type(self, logging_mock):
        bvd_data = RegistryData({
            "STANDARDISED_LEGAL_FORM": "Chocolate factory"
        })
        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertIsNone(metadata.structured_company_type)
        self.assertEqual(metadata.company_type, "Chocolate factory")
        self.assertTrue(logging_mock.error.called)


class TestIndustryClassification(TestCase):
    def test_uk_sic_code(self):
        bvd_data = RegistryData({
            "INDUSTRY_CLASSIFICATION": "UK SIC (2007)",
            "INDUSTRY_PRIMARY_CODE": [
                "62012"
            ],
            "INDUSTRY_PRIMARY_LABEL": [
                "Business and domestic software development"
            ],
        })

        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(
            metadata.industry_classifications,
            [IndustryClassification({
                "classification_type": IndustryClassificationType.SIC.value,
                "classification_version": "UK SIC (2007)",
                "code": "62012",
                "description": "Business and domestic software development",
            })]
        )

    def test_us_sic_code(self):
        bvd_data = RegistryData({
            "INDUSTRY_CLASSIFICATION": "US SIC",
            "INDUSTRY_PRIMARY_CODE": [
                "3674"
            ],
            "INDUSTRY_PRIMARY_LABEL": [
                "Semiconductors and related devices"
            ],
        })

        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(
            metadata.industry_classifications,
            [IndustryClassification({
                "classification_type": IndustryClassificationType.SIC.value,
                "classification_version": "US SIC",
                "code": "3674",
                "description": "Semiconductors and related devices",
            })]
        )


class TestCompanyNames(TestCase):
    def test_previous_names(self):
        bvd_data = RegistryData({
            "PREVIOUS_NAME": [
                "BLOCKOPS LIMITED"
            ],
            "PREVIOUS_NAME_DATE": [
                "2015-07-31T00:00:00"
            ],
        })

        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(
            metadata.previous_names,
            [
                PreviousName({
                    "name": "BLOCKOPS LIMITED",
                    "end": "2015-07-31T00:00:00",
                })
            ]
        )
