from unittest import TestCase

from app.api.formatter import entity_to_passfort_format, get_some_name

from swagger_client.models import Address, IndividualEntity, OrganisationEntity, Name, NameType, ActionDetail, \
    ProfileActionType, \
    ProviderSource, Role, \
    ProviderSourceStatus, ProviderSourceType, ProviderSourceTypeCategoryDetail, Country, CountryLink, CountryLinkType


bashar_uk_sanction = ActionDetail(
    action_type=ProfileActionType.SANCTION,
    text=" May 2011 - addition. Jun 2013 - amended. PRIMARY NAME: AL-ASSAD,BASHAR. DOB: 11/09/1965. "
         "POB: Damascus Passport Details: D1903 (Diplomatic) Position: President of the Republic. Group ID: 11928. ",
    title="UK",
    start_date=None,
    end_date=None,
    source=ProviderSource(abbreviation="UKHMT",
                          identifier="b_trwc_312",
                          provider_source_status=ProviderSourceStatus.ACTIVE,
                          name="UK - UKHMT - HM Treasury Sanctions Lists")
)

bashar_eu_sanction = ActionDetail(
    action_type=ProfileActionType.SANCTION,
    text=" EU 442/2011 (May 2011 - addition. Apr 2013 - amended). 2011/273/CFSP "
         "(May 2011 - addition. Apr 2013 - amended). "
         "PRIMARY NAME: Bashar Al-Assad. Identifying information: Date of birth: 11 September 1965; "
         "Place of birth: Damascus; "
         "diplomatic passport No D1903. "
         "Reasons: President of the Republic; person authorising and supervising the crackdown on demonstrators. ",
    title="EU",
    start_date=None,
    end_date=None,
    source=ProviderSource(abbreviation="OTHER SANCTIONS",
                          identifier="b_trwc_3",
                          provider_source_status=ProviderSourceStatus.HIDDEN,
                          name="World-Check Other Sanctions")
)

bashar_swiss_sanction = ActionDetail(
    action_type=ProfileActionType.SANCTION,
    text=" SSID: 200-11614 (May 2011 - addition. Jan 2016 - amended). PRIMARY NAME: Bashar Al-Assad DOB: 11 Sep 1965 "
         "POB: Damascus, Syrian Arab Republic Identification document: Diplomatic passport No. D1903, "
         "Syrian Arab Republic Justification: "
         "President of the Republic; person authorising and supervising the crackdown on demonstrators.",
    title="SWITZERLAND",
    start_date=None,
    end_date=None,
    source=ProviderSource(abbreviation="SECO",
                          identifier="t_trwc_2",
                          provider_source_status=ProviderSourceStatus.DELETED,
                          name="SWITZERLAND  - SECO - State Secretariat for Econ. Affairs.")
)

gazprom_canada_sanction = ActionDetail(
    action_type=ProfileActionType.SANCTION,
    text=" Jun 2015 - named on the unofficial list relating to Russia. "
         "Aug 2015 - list officially confirmed. PRIMARY NAME: OJSC Gazprom.",
    title="CANADA",
    start_date=None,
    end_date=None,
    source=ProviderSource(abbreviation="OTHER SANCTIONS",
                          identifier="b_trwc_3",
                          provider_source_status=ProviderSourceStatus.HIDDEN,
                          name="World-Check Other Sanction")
)

pep_source = ProviderSource(
    abbreviation="PEP N-R",
    creation_date="2013-03-21T13:41:09Z",
    name="PEP - National Government - Immediate Relative",
    identifier="b_trwc_PEP N-R",
    provider_source_status="ACTIVE",
    type=ProviderSourceType(
        category=ProviderSourceTypeCategoryDetail(
            description="This gives details of high-ranking government officials in over 200 countries. Although there "
                        "may be no reason why you should not do business with these individuals, the Basle Committee "
                        "on Banking supervision has stated that one should check these customers because without this "
                        "due diligence, banks can become subject to reputational, operational, legal and concentration "
                        "risks, which can result in significant financial cost.",
            name="PEP"
        ),
        identifier="t_trwc_8",
        name="National Government"
    )
)


class TestEntityFormatter(TestCase):

    def test_get_name(self):
        self.assertEqual(get_some_name(None), None)

        self.assertEqual(get_some_name(Name(given_name="James", last_name="Corden")), "Corden, James")
        self.assertEqual(get_some_name(Name()), ", ")

    def test_can_format_individual(self):
        with self.subTest("with primary name and alias"):
            entity = IndividualEntity(
                entity_id="e_tr_wci_1040772",
                entity_type="INDIVIDUAL",
                names=[
                    Name(full_name="John JONES", type=NameType.PRIMARY),
                    Name(full_name="JONES,John Mervyn", type=NameType.AKA)
                ])

            formatted_result = entity_to_passfort_format(entity)
            self.assertDictEqual(
                formatted_result,
                {
                    "match_id": "e_tr_wci_1040772",
                    "match_name": {"v": "John JONES"},
                    "aliases": [{"v": "JONES,John Mervyn"}],
                    "pep": {"v": {"match": False, "roles": []}},
                    "sanctions": [],
                    "sources": [],
                    "details": [],
                    "gender": {"v": None},
                    "deceased": {"v": False}
                })

        with self.subTest("without primary name or explicit alias"):
            entity = IndividualEntity(
                entity_id="e_tr_wci_1040772",
                entity_type="INDIVIDUAL",
                names=[
                    Name(full_name="John JONES"),
                    Name(full_name="JONES,John Mervyn")
                ])

            formatted_result = entity_to_passfort_format(entity)
            self.assertEqual(formatted_result["match_name"], {"v": None})
            self.assertIn({"v": "John JONES"}, formatted_result["aliases"])
            self.assertIn({"v": "JONES,John Mervyn"}, formatted_result["aliases"])

        with self.subTest("with nationality and addresses"):
            entity = IndividualEntity(
                entity_id="e_tr_wci_1040772",
                entity_type="INDIVIDUAL",
                names=[
                    Name(full_name="John JONES", type=NameType.PRIMARY),
                ],
                country_links=[
                    CountryLink(type=CountryLinkType.NATIONALITY, country=Country(code="GBR", name="United Kingdom")),
                    CountryLink(type=CountryLinkType.NATIONALITY, country=Country(code="ESP", name="Spain")),
                    CountryLink(type='LOCATION', country=Country(code="SYR", name="Syria")),
                    CountryLink(type=CountryLinkType.RESIDENT, country=Country(code="GBR", name="United Kingdom"))
                ],
                addresses=[
                    Address(country=Country(code="GBR", name="United Kingdom"), city="London", post_code="EC3N 4DR")
                ]
            )
            formatted_result = entity_to_passfort_format(entity)
            self.assertListEqual(formatted_result["match_countries"], [{"v": "GBR"}, {"v": "ESP"}])
            self.assertListEqual(
                formatted_result["match_countries_data"],
                [
                    {"country_code": "GBR", "type": "NATIONALITY"},
                    {"country_code": "ESP", "type": "NATIONALITY"},
                    {"country_code": "SYR", "type": "RESIDENCE"},
                ]
            )
            self.assertListEqual(
                formatted_result["locations"],
                [
                    {"v": {"type": "LOCATION", "country": "SYR"}},
                    {"v": {"type": "RESIDENT", "country": "GBR"}},
                    {"v": {"type": "ADDRESS", "country": "GBR", "city": "London", "address": "EC3N 4DR"}}
                ])

        with self.subTest("with pep roles and sanctions"):
            entity = IndividualEntity(
                entity_id="e_tr_wci_152",
                entity_type="INDIVIDUAL",
                names=[
                    Name(full_name="Bashar AL-ASSAD", type=NameType.PRIMARY),
                ],
                actions=[bashar_eu_sanction, bashar_swiss_sanction, bashar_uk_sanction],
                sources=[pep_source, bashar_eu_sanction.source, bashar_swiss_sanction.source, bashar_uk_sanction.source],
                roles=[Role(title="President of the Syrian Arab Republic")])
            formatted_result = entity_to_passfort_format(entity)

            self.assertDictEqual(
                formatted_result,
                {
                    "match_id": "e_tr_wci_152",
                    "match_name": {"v": "Bashar AL-ASSAD"},
                    "aliases": [],
                    "pep": {"v": {"match": True, "roles": [{"name": "President of the Syrian Arab Republic"}]}},
                    "sanctions": [
                        {
                            "v": {
                                "type": "SANCTION",
                                "list": bashar_eu_sanction.source.name,
                                "name": bashar_eu_sanction.text,
                                "issuer": "EU",
                                "is_current": True
                            }
                        },
                        {
                            "v": {
                                "type": "SANCTION",
                                "list": bashar_swiss_sanction.source.name,
                                "name": bashar_swiss_sanction.text,
                                "issuer": "SWITZERLAND",
                                "is_current": True
                            }
                        },
                        {
                            "v": {
                                "type": "SANCTION",
                                "list": bashar_uk_sanction.source.name,
                                "name": bashar_uk_sanction.text,
                                "issuer": "UK",
                                "is_current": True
                            }
                        }
                    ],
                    "sources": [
                        {
                            "v": {
                                "name": "PEP - National Government - Immediate Relative",
                                "description": pep_source.type.category.description
                            }
                        },
                        {
                            "v": {
                                "name": "World-Check Other Sanctions",
                                "description": None
                            }
                        },
                        {
                            "v": {
                                "name": "SWITZERLAND  - SECO - State Secretariat for Econ. Affairs.",
                                "description": None
                            }
                        },
                        {
                            "v": {
                                "name": "UK - UKHMT - HM Treasury Sanctions Lists",
                                "description": None
                            }
                        }
                    ],
                    "details": [],
                    "gender": {"v": None},
                    "deceased": {"v": False}
                })

    def test_can_format_company(self):
        with self.subTest("with name and aliases"):
            entity = OrganisationEntity(
                entity_id="e_tr_wco_2707386",
                entity_type="ORGANISATION",
                names=[
                    Name(full_name="ООО ГАЗПРОМ-МЕДИА", type=NameType.NATIVE_AKA),
                    Name(full_name="GAZPROM-MEDIA LLC", type=NameType.AKA),
                    Name(full_name="GAZPROM-MEDIA", type=NameType.PRIMARY)
                ])
    
            formatted_result = entity_to_passfort_format(entity)
            self.assertEqual(formatted_result["match_id"], "e_tr_wco_2707386")
            self.assertEqual(formatted_result["match_name"], {"v": "GAZPROM-MEDIA"})
            self.assertEqual(formatted_result["sanctions"], [])
            self.assertIn({"v": "ООО ГАЗПРОМ-МЕДИА"}, formatted_result["aliases"])
            self.assertIn({"v": "GAZPROM-MEDIA LLC"}, formatted_result["aliases"])

        with self.subTest("with country of incorporation and addresses"):
            entity = OrganisationEntity(
                entity_id="e_tr_wco_2707386",
                entity_type="ORGANISATION",
                names=[
                    Name(full_name="GAZPROM-MEDIA", type=NameType.PRIMARY),
                ],
                country_links=[
                    CountryLink(type=CountryLinkType.REGISTEREDIN,
                                country=Country(code="RUS", name="Russian Federation")),
                    CountryLink(type=CountryLinkType.OPERATESIN,
                                country=Country(code="RUS", name="Russian Federation"))
                ],
                addresses=[
                    Address(country=Country(code="RUS", name="Russian Federation"), city="Moscow")
                ]
            )
            formatted_result = entity_to_passfort_format(entity)
            self.assertListEqual(formatted_result["match_countries"], [{"v": "RUS"}])
            self.assertListEqual(
                formatted_result["locations"],
                [
                    {"v": {"type": "OPERATESIN", "country": "RUS"}},
                    {"v": {"type": "ADDRESS", "country": "RUS", "city": "Moscow", "address": None}}
                ])

        with self.subTest("with sanctions"):
            entity = OrganisationEntity(
                entity_id="e_tr_wco_9443",
                entity_type="ORGANISATION",
                names=[Name(full_name="GAZPROM-MEDIA", type=NameType.PRIMARY)],
                actions=[gazprom_canada_sanction]
            )

            formatted_result = entity_to_passfort_format(entity)
            self.assertEqual(
                formatted_result["sanctions"],
                [
                    {
                        "v": {
                            "type": "SANCTION",
                            "list": gazprom_canada_sanction.source.name,
                            "name": gazprom_canada_sanction.text,
                            "issuer": "CANADA",
                            "is_current": True
                        }
                    }
                ]
            )
