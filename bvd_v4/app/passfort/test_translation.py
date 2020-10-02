from datetime import date, datetime
from decimal import Decimal

import json
from mock import patch
from unittest import TestCase

from app.bvd.types import (
    Data,
    DataResult,
    OwnershipResult,
    RegistryData,
    RegistryResult,
)
from app.passfort.company_data import (
    Associate,
    CompanyData,
    IndividualAssociateData,
    Relationship,
    ShareholderRelationship,
)
from app.passfort.types import (
    CompanyMetadata,
    ContactDetails,
    IndustryClassification,
    IndustryClassificationType,
    OwnershipMetadata,
    PreviousName,
    Shareholding,
    TaxId,
    TaxIdType,
)
from app.passfort.structured_company_type import OwnershipType


class TestShareholders(TestCase):
    def test_individual_associated_entity(self):
        bvd_data = Data(
            {
                "BVD_ID_NUMBER": "GB09565115",
                "BVD9": "004954174",
                "SH_BVD_ID_NUMBER": ["GB*110178010270", "GB*110178010269"],
                "SH_ENTITY_TYPE": [
                    "One or more named individuals or families",
                    "One or more named individuals or families",
                ],
                "SH_NAME": ["MR FOO BAR BAZ", "DR JOHN SMITH"],
                "SH_FIRST_NAME": ["FOO BAR ", "JOHN"],
                "SH_LAST_NAME": ["BAZ", "SMITH"],
                "SH_UCI": ["P249742963", "P344359962"],
                "SH_COUNTRY_ISO_CODE": ["GB", "GB"],
                "SH_DIRECT_PCT": ["22.5", "19.63"],
            }
        )
        bvd_data.validate()

        company_data = CompanyData.from_bvd(bvd_data)
        company_data.validate()

        self.assertEqual(len(company_data.associated_entities), 2)

        first_shareholder = company_data.associated_entities[0]
        self.assertEqual(first_shareholder.immediate_data.entity_type, "INDIVIDUAL")
        self.assertEqual(
            first_shareholder.immediate_data.personal_details.name.title, "MR"
        )
        self.assertEqual(
            first_shareholder.immediate_data.personal_details.name.first_names,
            ["FOO", "BAR"],
        )
        self.assertEqual(
            first_shareholder.immediate_data.personal_details.name.last_name, "BAZ"
        )
        self.assertEqual(len(first_shareholder.relationships), 1)
        self.assertEqual(
            first_shareholder.relationships[0].relationship_type, "SHAREHOLDER"
        )
        self.assertEqual(
            first_shareholder.relationships[0].associated_role, "SHAREHOLDER"
        )
        self.assertEqual(
            first_shareholder.relationships[0].shareholdings[0].percentage,
            Decimal("0.225"),
        )
        second_shareholder = company_data.associated_entities[1]
        self.assertEqual(second_shareholder.immediate_data.entity_type, "INDIVIDUAL")
        self.assertEqual(
            second_shareholder.immediate_data.personal_details.name.title, "DR"
        )
        self.assertEqual(
            second_shareholder.immediate_data.personal_details.name.first_names,
            ["JOHN"],
        )
        self.assertEqual(
            second_shareholder.immediate_data.personal_details.name.last_name, "SMITH"
        )
        self.assertEqual(len(first_shareholder.relationships), 1)
        self.assertEqual(
            second_shareholder.relationships[0].relationship_type, "SHAREHOLDER"
        )
        self.assertEqual(
            second_shareholder.relationships[0].associated_role, "SHAREHOLDER"
        )
        self.assertEqual(
            second_shareholder.relationships[0].shareholdings[0].percentage,
            Decimal("0.1963"),
        )


class TestOfficers(TestCase):
    def test_individual_associated_entity(self):
        bvd_data = Data(
            {
                "BVD_ID_NUMBER": "GB09565115",
                "BVD9": "004954174",
                "CPYCONTACTS_HEADER_Type": ["Individual", "Individual", "Individual"],
                "CPYCONTACTS_HEADER_BvdId": [None, None, None],
                "CPYCONTACTS_HEADER_IdDirector": [
                    "P045831593",
                    "P045831593",
                    "P045831593",
                ],
                "CPYCONTACTS_MEMBERSHIP_Function": [
                    "Director (occupation: Chief Executive)",
                    "Chief Executive Officer - Executive Contact",
                    "Manager - General Contact",
                ],
                "CPYCONTACTS_MEMBERSHIP_EndExpirationDate": [
                    None,
                    "2018-12-31T00:00:00",
                    None,
                ],
                "CPYCONTACTS_HEADER_FirstNameOriginalLanguagePreferred": [
                    None,
                    None,
                    None,
                ],
                "CPYCONTACTS_HEADER_MiddleNameOriginalLanguagePreferred": [
                    None,
                    None,
                    None,
                ],
                "CPYCONTACTS_HEADER_LastNameOriginalLanguagePreferred": [
                    None,
                    None,
                    None,
                ],
                "CPYCONTACTS_HEADER_FullNameOriginalLanguagePreferred": [
                    "Mr Timothy Deighton Steiner",
                    "Mr Timothy Deighton Steiner",
                    "Mr Timothy Deighton Steiner",
                ],
                "CPYCONTACTS_HEADER_Birthdate": [
                    "1969-12-09T00:00:00",
                    "1969-12-09T00:00:00",
                    "1969-12-09T00:00:00",
                ],
                "CPYCONTACTS_HEADER_NationalityCountryLabel": [
                    "United Kingdom",
                    "United Kingdom",
                    "United Kingdom",
                ],
                "CPYCONTACTS_MEMBERSHIP_BeginningNominationDate": [
                    "2000-04-13T00:00:00",
                    None,
                    None,
                ],
            }
        )
        bvd_data.validate()

        company_data = CompanyData.from_bvd(bvd_data)
        company_data.validate()

        self.assertEqual(len(company_data.associated_entities), 1)

        officer = company_data.associated_entities[0]
        self.assertEqual(officer.entity_type, "INDIVIDUAL")
        self.assertEqual(len(officer.relationships), 3)

        self.assertEqual(officer.immediate_data.entity_type, "INDIVIDUAL")
        self.assertEqual(officer.immediate_data.personal_details.name.title, "Mr")

        self.assertEqual(
            officer.immediate_data.personal_details.name.first_names,
            ["Timothy", "Deighton"],
        )
        self.assertEqual(
            officer.immediate_data.personal_details.name.last_name, "Steiner"
        )
        self.assertEqual(
            officer.immediate_data.personal_details.dob, datetime(1969, 12, 9)
        )
        self.assertEqual(officer.immediate_data.personal_details.nationality, "GBR")

        self.assertEqual(len(officer.relationships), 3)
        self.assertTrue(
            all(rel.relationship_type == "OFFICER" for rel in officer.relationships)
        )

        self.assertEqual(officer.relationships[0].associated_role, "DIRECTOR")
        self.assertEqual(
            officer.relationships[0].original_role,
            "Director (occupation: Chief Executive)",
        )
        self.assertEqual(officer.relationships[0].appointed_on, date(2000, 4, 13))

        self.assertEqual(officer.relationships[1].associated_role, "RESIGNED_OFFICER")
        self.assertEqual(
            officer.relationships[1].original_role,
            "Chief Executive Officer - Executive Contact",
        )
        self.assertIsNone(officer.relationships[1].appointed_on)

        self.assertEqual(officer.relationships[2].associated_role, "OTHER")
        self.assertEqual(
            officer.relationships[2].original_role, "Manager - General Contact"
        )
        self.assertIsNone(officer.relationships[2].appointed_on)

    def test_company_associated_entity(self):
        bvd_data = Data(
            {
                "BVD_ID_NUMBER": "GB09565115",
                "BVD9": "004954174",
                "CPYCONTACTS_HEADER_Type": ["Company"],
                "CPYCONTACTS_HEADER_BvdId": ["GB02734789"],
                "CPYCONTACTS_HEADER_IdDirector": ["C004368396"],
                "CPYCONTACTS_MEMBERSHIP_Function": ["Company Secretary"],
                "CPYCONTACTS_MEMBERSHIP_EndExpirationDate": ["2000-02-02T00:00:00"],
                "CPYCONTACTS_HEADER_FirstNameOriginalLanguagePreferred": [None],
                "CPYCONTACTS_HEADER_MiddleNameOriginalLanguagePreferred": [None],
                "CPYCONTACTS_HEADER_LastNameOriginalLanguagePreferred": [None],
                "CPYCONTACTS_HEADER_FullNameOriginalLanguagePreferred": [
                    "PAILEX CORPORATE SERVICES LIMITED",
                ],
                "CPYCONTACTS_HEADER_Birthdate": [None],
                "CPYCONTACTS_HEADER_NationalityCountryLabel": [None],
                "CPYCONTACTS_MEMBERSHIP_BeginningNominationDate": [
                    "1999-11-11T00:00:00",
                ],
            }
        )
        bvd_data.validate()

        company_data = CompanyData.from_bvd(bvd_data)
        company_data.validate()

        self.assertEqual(len(company_data.associated_entities), 1)

        officer = company_data.associated_entities[0]
        self.assertEqual(officer.entity_type, "COMPANY")
        self.assertEqual(len(officer.relationships), 1)

        self.assertEqual(officer.immediate_data.entity_type, "COMPANY")
        self.assertEqual(
            officer.immediate_data.metadata.name, "PAILEX CORPORATE SERVICES LIMITED"
        )
        self.assertEqual(officer.immediate_data.metadata.bvd_id, "GB02734789")

        self.assertEqual(len(officer.relationships), 1)
        self.assertEqual(officer.relationships[0].relationship_type, "OFFICER")
        self.assertEqual(officer.relationships[0].associated_role, "RESIGNED_OFFICER")


class TestMergeAssociates(TestCase):
    def test_merge(self):
        associate_a = Associate(
            {
                "associate_id": "863318d7-3176-3348-95fd-4de0a2fe1ad6",
                "entity_type": "INDIVIDUAL",
                "immediate_data": IndividualAssociateData(
                    {
                        "entity_type": "INDIVIDUAL",
                        "personal_details": {
                            "name": {
                                "first_names": ["John"],
                                "last_name": "Smith",
                                "title": "Mr",
                            },
                            "nationality": "GBR",
                        },
                    }
                ),
                "relationships": [
                    ShareholderRelationship(
                        {
                            "associated_role": "SHAREHOLDER",
                            "relationship_type": "SHAREHOLDER",
                            "shareholdings": [
                                Shareholding({"percentage": Decimal("0.25")})
                            ],
                        }
                    )
                ],
            }
        )

        associate_b = Associate(
            {
                "associate_id": "863318d7-3176-3348-95fd-4de0a2fe1ad6",
                "entity_type": "INDIVIDUAL",
                "immediate_data": IndividualAssociateData(
                    {
                        "entity_type": "INDIVIDUAL",
                        "personal_details": {
                            "name": {
                                "first_names": ["JOHN"],
                                "last_name": "SMITH",
                                "title": "Mr",
                            },
                            "nationality": "GBR",
                        },
                    }
                ),
                "relationships": [
                    {"associated_role": "DIRECCTOR", "relationship_type": "OFFICER"}
                ],
            }
        )

        merged = Associate.merge(associate_a, associate_b)

        self.assertEqual(merged.associate_id, associate_a.associate_id)
        self.assertEqual(merged.entity_type, associate_a.entity_type)
        self.assertEqual(
            merged.immediate_data.personal_details.name.title,
            associate_a.immediate_data.personal_details.name.title,
        )
        self.assertEqual(
            merged.immediate_data.personal_details.name.first_names,
            associate_a.immediate_data.personal_details.name.first_names,
        )
        self.assertEqual(
            merged.immediate_data.personal_details.name.last_name,
            associate_a.immediate_data.personal_details.name.last_name,
        )
        self.assertEqual(
            merged.immediate_data.personal_details.nationality,
            associate_a.immediate_data.personal_details.nationality,
        )
        self.assertEqual(
            merged.relationships,
            [
                ShareholderRelationship(
                    {
                        "associated_role": "SHAREHOLDER",
                        "relationship_type": "SHAREHOLDER",
                        "shareholdings": [
                            Shareholding({"percentage": Decimal("0.25")})
                        ],
                    }
                ),
                Relationship(
                    {"associated_role": "DIRECCTOR", "relationship_type": "OFFICER"}
                ),
            ],
        )


class TestMetadata(TestCase):
    def test_company_data_check(self):
        with open("./demo_data/company_data/pass.json") as demo_file:
            bvd_result = DataResult(json.load(demo_file))
            bvd_result.validate()

            metadata = CompanyMetadata.from_bvd(bvd_result.data[0])
            metadata.validate()

            self.assertEqual(metadata.bvd_id, "pass")
            self.assertEqual(metadata.number, "09565115")
            self.assertEqual(metadata.bvd9, "230418860")
            self.assertIsNone(metadata.isin)
            self.assertIsNone(metadata.lei)
            self.assertEqual(
                metadata.tax_ids,
                [TaxId({"tax_id_type": TaxIdType.EUROVAT.value, "value": "n.a."})],
            )
            self.assertEqual(metadata.name, "PASSFORT LIMITED")
            self.assertEqual(
                metadata.contact_information.url, "www.passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.email, "info@passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.phone_number, "+44 20 3633 1761",
            )
            self.assertEqual(
                metadata.freeform_address,
                "MEZZANINE FLOOR 24 CORNHILL, EC3V 3ND, LONDON, United Kingdom",
            )
            self.assertTrue(metadata.is_active)
            self.assertEqual(metadata.is_active_details, "Active")
            self.assertEqual(
                metadata.trade_description, "Business and domestic software development"
            )
            self.assertIsNone(metadata.description)

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
                [TaxId({"tax_id_type": TaxIdType.EUROVAT.value, "value": "n.a."})],
            )
            self.assertEqual(metadata.name, "PASSFORT LIMITED")
            self.assertEqual(
                metadata.contact_information.url, "www.passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.email, "info@passfort.com",
            )
            self.assertEqual(
                metadata.contact_information.phone_number, "+44 20 3633 1761",
            )
            self.assertEqual(
                metadata.freeform_address,
                "MEZZANINE FLOOR 24 CORNHILL, EC3V 3ND, LONDON, United Kingdom",
            )
            self.assertTrue(metadata.is_active)
            self.assertEqual(metadata.is_active_details, "Active")
            self.assertEqual(
                metadata.trade_description, "Business and domestic software development"
            )
            self.assertIsNone(metadata.description)

    def test_ownership_check(self):
        with open("./demo_data/ownership/pass.json") as demo_file:
            bvd_result = OwnershipResult(json.load(demo_file))
            bvd_result.validate()

            metadata = OwnershipMetadata.from_bvd(bvd_result.data[0])
            metadata.validate()
            self.assertEqual(metadata.company_type, "Private limited companies")
            self.assertFalse(metadata.structured_company_type.is_public)
            self.assertTrue(metadata.structured_company_type.is_limited)
            self.assertEqual(
                metadata.structured_company_type.ownership_type,
                OwnershipType.COMPANY.value,
            )


class TestCompanyType(TestCase):
    def test_company_type(self):
        bvd_data = RegistryData(
            {"STANDARDISED_LEGAL_FORM": "Private limited companies"}
        )
        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(metadata.company_type, "Private limited companies")

    def test_known_structured_company_type(self):
        bvd_data = RegistryData(
            {"STANDARDISED_LEGAL_FORM": "Private limited companies"}
        )
        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertFalse(metadata.structured_company_type.is_public)
        self.assertTrue(metadata.structured_company_type.is_limited)
        self.assertEqual(
            metadata.structured_company_type.ownership_type, OwnershipType.COMPANY.value
        )

    @patch("app.passfort.structured_company_type.logging")
    def test_unknown_structured_company_type(self, logging_mock):
        bvd_data = RegistryData({"STANDARDISED_LEGAL_FORM": "Chocolate factory"})
        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertIsNone(metadata.structured_company_type)
        self.assertEqual(metadata.company_type, "Chocolate factory")
        self.assertTrue(logging_mock.error.called)


class TestIndustryClassification(TestCase):
    def test_uk_sic_code(self):
        bvd_data = RegistryData(
            {
                "INDUSTRY_CLASSIFICATION": "UK SIC (2007)",
                "INDUSTRY_PRIMARY_CODE": ["62012"],
                "INDUSTRY_PRIMARY_LABEL": [
                    "Business and domestic software development"
                ],
            }
        )

        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(
            metadata.industry_classifications,
            [
                IndustryClassification(
                    {
                        "classification_type": IndustryClassificationType.SIC.value,
                        "classification_version": "UK SIC (2007)",
                        "code": "62012",
                        "description": "Business and domestic software development",
                    }
                )
            ],
        )

    def test_us_sic_code(self):
        bvd_data = RegistryData(
            {
                "INDUSTRY_CLASSIFICATION": "US SIC",
                "INDUSTRY_PRIMARY_CODE": ["3674"],
                "INDUSTRY_PRIMARY_LABEL": ["Semiconductors and related devices"],
            }
        )

        metadata = CompanyMetadata.from_bvd(bvd_data)

        self.assertEqual(
            metadata.industry_classifications,
            [
                IndustryClassification(
                    {
                        "classification_type": IndustryClassificationType.SIC.value,
                        "classification_version": "US SIC",
                        "code": "3674",
                        "description": "Semiconductors and related devices",
                    }
                )
            ],
        )


class TestCompanyNames(TestCase):
    def test_previous_names(self):
        bvd_data = RegistryData(
            {
                "PREVIOUS_NAME": ["BLOCKOPS LIMITED"],
                "PREVIOUS_NAME_DATE": ["2015-07-31T00:00:00"],
            }
        )

        metadata = CompanyMetadata.from_bvd(bvd_data)
        self.assertEqual(
            metadata.previous_names,
            [PreviousName({"name": "BLOCKOPS LIMITED", "end": "2015-07-31T00:00:00"})],
        )
