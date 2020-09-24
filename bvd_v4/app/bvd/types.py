from schematics import Model
from schematics.exceptions import BaseError, ValidationError, ConversionError, CompoundError
from schematics.types import (
    FloatType,
    StringType,
    DateTimeType,
    ListType,
    PolyModelType,
    IntType,
    BaseType,
    ModelType,
)

from app.bvd.maybe_list import MaybeListType


class RegistryData(Model):
    # Idenification
    bvd_id = StringType(serialized_name="BVD_ID_NUMBER", required=True)
    trade_register_number = MaybeListType(StringType(), serialized_name="TRADE_REGISTER_NUMBER")
    bvd9 = StringType(serialized_name="BVD9", required=True)
    name = StringType(serialized_name="NAME", default=None)
    previous_names = MaybeListType(StringType(), serialized_name="PREVIOUS_NAME", default=list, required=True)
    previous_dates = MaybeListType(DateTimeType(), serialized_name="PREVIOUS_NAME_DATE", default=list, required=True)
    isin = StringType(serialized_name="ISIN", default=None)
    lei = StringType(serialized_name="LEI", default=None)
    vat = StringType(serialized_name="VAT", default=None)
    eurovat = StringType(serialized_name="EUROVAT", default=None)
    irs = StringType(serialized_name="IRS", default=None)

    # Contact Details
    website = MaybeListType(StringType(), serialized_name="WEBSITE", default=list)
    phone_number = MaybeListType(StringType(), serialized_name="PHONE_NUMBER")
    email = MaybeListType(StringType(), serialized_name="EMAIL")

    # Address
    address_type = StringType(serialized_name="ADDRESS_TYPE")
    address_line_one = StringType(serialized_name="ADDRESS_LINE1")
    address_line_two = StringType(serialized_name="ADDRESS_LINE2", default=None)
    address_line_three = StringType(serialized_name="ADDRESS_LINE3", default=None)
    address_line_four = StringType(serialized_name="ADDRESS_LINE4", default=None)
    postcode = StringType(serialized_name="POSTCODE", default=None)
    city = StringType(serialized_name="CITY", default=None)
    country_region = MaybeListType(StringType(), serialized_name="COUNTRY_REGION", default=list)
    state = StringType(serialized_name="US_STATE", default=None)
    incorporation_state = StringType(serialized_name="INCORPORATION_STATE", default=None)
    country = StringType(serialized_name="COUNTRY", default=None)
    country_code = StringType(serialized_name="COUNTRY_ISO_CODE", default=None)
    longitude = FloatType(serialized_name="LONGITUDE", default=None)
    latitude = FloatType(serialized_name="LATITUDE", default=None)

    # Classification
    status = MaybeListType(StringType(), serialized_name="STATUS", default=list)
    standardised_legal_form = StringType(serialized_name="STANDARDISED_LEGAL_FORM", default=None)
    products_services = StringType(serialized_name="PRODUCTS_SERVICES", default=None)
    trade_description_english = StringType(serialized_name="TRADE_DESCRIPTION_EN", default=None)
    trade_description_original_lang = StringType(
        serialized_name="TRADE_DESCRIPTION_ORIGINAL",
        default=None
    )
    industry_classification = StringType(serialized_name="INDUSTRY_CLASSIFICATION", default=None)
    industry_primary_code = MaybeListType(
        StringType(), serialized_name="INDUSTRY_PRIMARY_CODE", default=list
    )
    industry_primary_label = MaybeListType(
        StringType(), serialized_name="INDUSTRY_PRIMARY_LABEL", default=list
    )
    industry_secondary_code = MaybeListType(
        StringType(), serialized_name="INDUSTRY_SECONDARY_CODE", default=list
    )
    industry_secondary_label = MaybeListType(
        StringType(), serialized_name="INDUSTRY_SECONDARY_LABEL", default=list
    )

    @property
    def address_fields(self):
        return [
            'address_line_one',
            'address_line_two',
            'address_line_three',
            'address_line_four',
            'postcode',
            'city',
            'country',
        ]

    @property
    def freeform_address(self):
        return ', '.join(
            getattr(self, field)
            for field in self.address_fields
            if getattr(self, field) is not None
        )


class OwnershipData(Model):
    standardised_legal_form = StringType(serialized_name="STANDARDISED_LEGAL_FORM", default=None)

    shareholder_entity_type = ListType(StringType(), serialized_name="SH_ENTITY_TYPE", default=list, required=True)
    shareholder_bvd_id = ListType(StringType(), serialized_name="SH_BVD_ID_NUMBER", default=list, required=True)
    shareholder_bvd9 = ListType(StringType(), serialized_name="SH_BVD9", default=list)
    shareholder_uci = ListType(StringType(), serialized_name="SH_UCI", default=list)
    shareholder_lei = ListType(StringType(), serialized_name="SH_LEI", default=list)

    shareholder_country_code = ListType(StringType(), serialized_name="SH_COUNTRY_ISO_CODE", default=list)
    shareholder_state_province = ListType(StringType(), serialized_name="SH_STATE_PROVINCE", default=list)
    shareholder_state_province = ListType(StringType(), serialized_name="SH_STATE_PROVINCE", default=list)
    shareholder_name = ListType(StringType(), serialized_name="SH_NAME", default=list)
    shareholder_first_name = ListType(StringType(), serialized_name="SH_FIRST_NAME", default=list)
    shareholder_last_name = ListType(StringType(), serialized_name="SH_LAST_NAME", default=list)

    shareholder_direct_percentage = ListType(StringType(), serialized_name="SH_DIRECT_PCT", default=list)

    beneficial_owner_bvd_id = ListType(StringType(), serialized_name="BO_BVD_ID_NUMBER", default=list)
    beneficial_owner_uci = ListType(StringType(), serialized_name="BO_UCI", default=list)
    beneficial_owner_entity_type = ListType(StringType(), serialized_name="BO_ENTITY_TYPE", default=list)
    beneficial_owner_country_code = ListType(StringType(), serialized_name="BO_COUNTRY_ISO_CODE", default=list)
    beneficial_owner_name = ListType(StringType(), serialized_name="BO_NAME", default=list)
    beneficial_owner_first_name = ListType(StringType(), serialized_name="BO_FIRST_NAME", default=list)
    beneficial_owner_last_name = ListType(StringType(), serialized_name="BO_LAST_NAME", default=list)
    beneficial_owner_birth_date = ListType(DateTimeType(), serialized_name="BO_BIRTHDATE", default=list)

    def shareholder_is_individual(self, index):
        return self.shareholder_entity_type[index] == 'One or more named individuals or families'

    def beneficial_owner_is_individual(self, index):
        return self.beneficial_owner_entity_type[index] == 'One or more named individuals or families'


class Match(Model):
    name = StringType(serialized_name="NAME", required=True)
    name_international = StringType(serialized_name="NAME_INTERNATIONAL", default=None)
    bvd9 = StringType(serialized_name="BVD9", required=True, default=None)
    status = StringType(serialized_name="STATUS", required=True)
    address_type = StringType(serialized_name="ADDRESS_TYPE", default=None)
    address = StringType(serialized_name="ADDRESS", default=None)
    postcode = StringType(serialized_name="POSTCODE", default=None)
    city = StringType(serialized_name="CITY", default=None)
    country = StringType(serialized_name="COUNTRY", required=True, default=None)
    state = StringType(serialized_name='STATE', default=None)
    national_id = StringType(serialized_name="NATIONAL_ID", default=None)
    hint = StringType(serialized_name="HINT", default=None)
    score = FloatType(serialized_name="SCORE", default=None)


class WrappedMatch(Model):
    zero = ModelType(Match, serialized_name="0", required=True)


class SearchData(Model):
    bvd_id = StringType(serialized_name="BVDID", required=True)
    match = ModelType(WrappedMatch, serialized_name="MATCH", required=True)


class DatabaseInfo(Model):
    version_number = StringType(serialized_name="VersionNumber")
    update_date = StringType(serialized_name="UpdateDate")
    update_number = StringType(serialized_name="UpdateNumber")
    release_number = StringType(serialized_name="ReleaseNumber")


class SearchSummary(Model):
    database_info = ModelType(DatabaseInfo, serialized_name="DatabaseInfo")
    records_returned = IntType(serialized_name="RecordsReturned", required=True)
    offset = IntType(serialized_name="Offset", required=True)
    total_records_found = IntType(serialized_name="TotalRecordsFound", required=True)


class Data(RegistryData, OwnershipData):
    pass


class DataResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = MaybeListType(ModelType(Data), serialized_name="Data")


class RegistryResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = MaybeListType(ModelType(RegistryData), serialized_name="Data")


class OwnershipResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = ListType(ModelType(OwnershipData), serialized_name="Data")


class SearchResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = MaybeListType(ModelType(SearchData), serialized_name="Data", required=True)
