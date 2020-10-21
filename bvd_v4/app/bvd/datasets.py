from enum import Enum

UPDATE_FIELDS = {
    "BVD_ID_NUMBER",
    "NAME_UPDATE",
    "ADDRESS_UPDATE",
    "STATUS_UPDATE",
}

OFFICERS_FIELDS = {
    "CPYCONTACTS_HEADER_BvdId",  # bvd_ids
    "CPYCONTACTS_HEADER_IdDirector",  # officer_ucis
    "CPYCONTACTS_MEMBERSHIP_CurrentPrevious",
    "CPYCONTACTS_MEMBERSHIP_Function",
    "CPYCONTACTS_MEMBERSHIP_BeginningNominationDate",  # appointment date
    "CPYCONTACTS_MEMBERSHIP_EndExpirationDate",  # Resignation date
    "CPYCONTACTS_HEADER_Type",
    "CPYCONTACTS_HEADER_BareTitle",
    "CPYCONTACTS_HEADER_FirstNameOriginalLanguagePreferred",
    "CPYCONTACTS_HEADER_MiddleNameOriginalLanguagePreferred",
    "CPYCONTACTS_HEADER_LastNameOriginalLanguagePreferred",
    "CPYCONTACTS_HEADER_FullNameOriginalLanguagePreferred",
    "CPYCONTACTS_HEADER_NationalityCountryLabel",
    "CPYCONTACTS_HEADER_Birthdate",
}

REGISTRY_FIELDS = {
    "BVD_ID_NUMBER",
    "BVD9",
    "LEI",
    "ISIN",
    "TRADE_REGISTER_NUMBER",
    "VAT_NUMBER",
    "EUROPEAN_VAT_NUMBER",
    # TODO: Where can we get this field now?
    # "IRS"
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
}


OWNERSHIP_FIELDS = {
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
    "BO_COUNTRY_ISO_CODE",
    "BO_UCI",
    "BO_ENTITY_TYPE",
    "BO_NAME",
    "BO_FIRST_NAME",
    "BO_LAST_NAME",
    "BO_BIRTHDATE",
}


class DataSet(Enum):
    ALL = "ALL"
    REGISTRY = "REGISTRY"
    OWNERSHIP = "OWNERSHIP"
    OFFICERS = "OFFICERS"
    UPDATE = "UPDATE"

    @property
    def data_fields(self):
        if self == DataSet.ALL:
            return list(
                {
                    field
                    for data_set in DataSet
                    if data_set != DataSet.ALL
                    for field in data_set.data_fields
                }
            )
        elif self == DataSet.REGISTRY:
            return list(REGISTRY_FIELDS)
        elif self == DataSet.OWNERSHIP:
            return list(OWNERSHIP_FIELDS)
        elif self == DataSet.OFFICERS:
            return list(OFFICERS_FIELDS)
        elif self == DataSet.UPDATE:
            return list(UPDATE_FIELDS)

    @property
    def update_query(self):
        if self == DataSet.REGISTRY:
            return {"General": ["1", "2", "8"]}
        elif self == DataSet.OFFICERS:
            return {
                "UpdatedCompaniesBasedOnMembershipsWithWocoFlags": [
                    "COMMON_DIRECTORS_00",
                    "COMMON_DIRECTORS_01",
                    "COMMON_DIRECTORS_02",
                    "COMMON_DIRECTORS_09",
                ],
            }
        elif self == DataSet.OWNERSHIP:
            return {
                "UpdatedWoco4OwnerShip": ["Ownership_bo_w", "Ownership_wof",],
            }
