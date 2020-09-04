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
            return []
