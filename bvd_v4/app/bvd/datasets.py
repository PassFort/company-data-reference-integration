from enum import Enum


REGISTRY_FIELDS = [
    "BVD_ID_NUMBER",
    "BVD9",
    "LEI",
    "ISIN",
    "TRADE_REGISTER_NUMBER",

    "NAME",
    "PREVIOUS_NAME",
    "PREVIOUS_NAME_DATE",
    "WEBSITE",
    "PHONE_NUMBER",
    "EMAIL",

    "ADDRESS_LINE1",
    "ADDRESS_LINE2",
    "ADDRESS_LINE3",
    "ADDRESS_LINE4",
    "POSTCODE",
    "CITY",
    "COUNTRY",
    "COUNTRY_ISO_CODE",
    "LATITUDE",
    "LONGITUDE",
    "COUNTRY_REGION",
    "US_STATE",
    "ADDRESS_TYPE",

    "STATUS",
    "STANDARDISED_LEGAL_FORM",
    "PRODUCTS_SERVICES",
    "TRADE_DESCRIPTION_EN",
    "TRADE_DESCRIPTION_ORIGINAL",
    "INDUSTRY_CLASSIFICATION",
    "INDUSTRY_PRIMARY_CODE",
    "INDUSTRY_PRIMARY_LABEL",
    "INDUSTRY_SECONDARY_CODE",
    "INDUSTRY_SECONDARY_LABEL",
]

OWNERSHIP_FIELDS = [
    # Metadata
    "STANDARDISED_LEGAL_FORM",

    # Shareholders
    "SH_ENTITY_TYPE",
    "SH_BVD_ID_NUMBER",
    "SH_BVD9",
    "SH_UCI",
    "SH_LEI",
    "SH_COUNTRY_ISO_CODE",
    "SH_STATE_PROVINCE",
    "SH_NAME",
    "SH_FIRST_NAME",
    "SH_LAST_NAME",
    "SH_DIRECT_PCT",

    # Beneficial Owners
    "BO_BVD_ID_NUMBER",
    "BO_UCI",
    "BO_ENTITY_TYPE",
    "BO_NAME",
    "BO_FIRST_NAME",
    "BO_LAST_NAME",
    "BO_BIRTHDATE",
]


class DataSet(Enum):
    ALL = "ALL"
    REGISTRY = "REGISTRY"
    OWNERSHIP = "OWNERSHIP"

    @property
    def fields(self):
        if self == DataSet.ALL:
            return [
                field
                for data_set in DataSet
                if data_set != DataSet.ALL
                for field in data_set.fields
            ]
        elif self == DataSet.REGISTRY:
            return REGISTRY_FIELDS
        elif self == DataSet.OWNERSHIP:
            return OWNERSHIP_FIELDS
