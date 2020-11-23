import logging

from schematics import Model
from schematics.exceptions import (
    BaseError,
    ValidationError,
    ConversionError,
    CompoundError,
)
from schematics.types import (
    BaseType,
    BooleanType,
    DictType,
    FloatType,
    StringType,
    DateTimeType,
    ListType,
    PolyModelType,
    IntType,
    ModelType,
    UUIDType,
)

from app.bvd.maybe_list import MaybeListType
from app.common import build_resolver_id


class RegistryData(Model):
    # Idenification
    bvd_id = StringType(serialized_name="BVD_ID_NUMBER", required=True)
    trade_register_number = MaybeListType(
        StringType(), serialized_name="TRADE_REGISTER_NUMBER", default=None
    )
    bvd9 = StringType(serialized_name="BVD9", required=True)
    name = StringType(serialized_name="NAME", default=None)
    previous_names = MaybeListType(
        StringType(), serialized_name="PREVIOUS_NAME", default=list, required=True
    )
    previous_dates = MaybeListType(
        DateTimeType(),
        serialized_name="PREVIOUS_NAME_DATE",
        default=list,
        required=True,
    )
    isin = StringType(serialized_name="ISIN", default=None)
    lei = StringType(serialized_name="LEI", default=None)
    vat = MaybeListType(
        StringType(), serialized_name="VAT_NUMBER", default=list, required=True
    )
    eurovat = MaybeListType(
        StringType(), serialized_name="EUROPEAN_VAT_NUMBER", default=list, required=True
    )
    irs = StringType(serialized_name="IRS", default=None)

    # Contact Details
    website = MaybeListType(StringType(), serialized_name="WEBSITE", default=list)
    phone_number = MaybeListType(
        StringType(), serialized_name="PHONE_NUMBER", default=list
    )
    email = MaybeListType(StringType(), serialized_name="EMAIL", default=list)

    # Address
    address_type = StringType(serialized_name="ADDRESS_TYPE")
    address_line_one = StringType(serialized_name="ADDRESS_LINE1", default=None)
    address_line_two = StringType(serialized_name="ADDRESS_LINE2", default=None)
    address_line_three = StringType(serialized_name="ADDRESS_LINE3", default=None)
    address_line_four = StringType(serialized_name="ADDRESS_LINE4", default=None)
    postcode = StringType(serialized_name="POSTCODE", default=None)
    city = StringType(serialized_name="CITY", default=None)
    country_region = MaybeListType(
        StringType(), serialized_name="COUNTRY_REGION", default=list
    )
    state = StringType(serialized_name="US_STATE", default=None)
    incorporation_state = StringType(
        serialized_name="INCORPORATION_STATE", default=None
    )
    incorporation_date = StringType(serialized_name="INCORPORATION_DATE", default=None)
    country = StringType(serialized_name="COUNTRY", default=None)
    country_code = StringType(serialized_name="COUNTRY_ISO_CODE", default=None)
    longitude = FloatType(serialized_name="LONGITUDE", default=None)
    latitude = FloatType(serialized_name="LATITUDE", default=None)

    # Classification
    status = MaybeListType(StringType(), serialized_name="STATUS", default=list)
    standardised_legal_form = StringType(
        serialized_name="STANDARDISED_LEGAL_FORM", default=None
    )
    products_services = StringType(serialized_name="PRODUCTS_SERVICES", default=None)
    trade_description_english = StringType(
        serialized_name="TRADE_DESCRIPTION_EN", default=None
    )
    trade_description_original_lang = StringType(
        serialized_name="TRADE_DESCRIPTION_ORIGINAL", default=None
    )
    industry_classification = StringType(
        serialized_name="INDUSTRY_CLASSIFICATION", default=None
    )
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
    us_sic_core_code = MaybeListType(
        StringType(), serialized_name="USSIC_CORE_CODE", default=list
    )
    us_sic_core_label = MaybeListType(
        StringType(), serialized_name="USSIC_CORE_LABEL", default=list
    )
    nace2_core_code = MaybeListType(
        StringType(), serialized_name="NACE2_CORE_CODE", default=list
    )
    nace2_core_label = MaybeListType(
        StringType(), serialized_name="NACE2_CORE_LABEL", default=list
    )
    naics2017_core_code = MaybeListType(
        StringType(), serialized_name="NAICS2017_CORE_CODE", default=list
    )
    naics2017_core_label = MaybeListType(
        StringType(), serialized_name="NAICS2017_CORE_LABEL", default=list
    )
    # Officers
    contact_bvd_id = MaybeListType(
        StringType(), serialized_name="CPYCONTACTS_HEADER_BvdId", default=list
    )
    contact_uci = MaybeListType(
        StringType(), serialized_name="CPYCONTACTS_HEADER_IdDirector", default=list
    )
    contact_entity_type = MaybeListType(
        StringType(), serialized_name="CPYCONTACTS_HEADER_Type", default=list
    )
    contact_role = MaybeListType(
        StringType(), serialized_name="CPYCONTACTS_MEMBERSHIP_Function", default=list
    )
    contact_title = MaybeListType(
        StringType(), serialized_name="CPYCONTACTS_HEADER_BareTitle", default=list,
    )
    contact_first_name = MaybeListType(
        StringType(),
        serialized_name="CPYCONTACTS_HEADER_FirstNameOriginalLanguagePreferred",
        default=list,
    )
    contact_middle_name = MaybeListType(
        StringType(),
        serialized_name="CPYCONTACTS_HEADER_MiddleNameOriginalLanguagePreferred",
        default=list,
    )
    contact_last_name = MaybeListType(
        StringType(),
        serialized_name="CPYCONTACTS_HEADER_LastNameOriginalLanguagePreferred",
        default=list,
    )
    contact_name = MaybeListType(
        StringType(),
        serialized_name="CPYCONTACTS_HEADER_FullNameOriginalLanguagePreferred",
        default=list,
    )
    contact_nationality = MaybeListType(
        StringType(),
        serialized_name="CPYCONTACTS_HEADER_NationalityCountryLabel",
        default=list,
    )
    contact_current_previous = MaybeListType(
        StringType(choices=["Current", "Previous"]),
        serialized_name="CPYCONTACTS_MEMBERSHIP_CurrentPrevious",
        default=list,
    )
    contact_resignation_date = MaybeListType(
        DateTimeType(),
        serialized_name="CPYCONTACTS_MEMBERSHIP_EndExpirationDate",
        default=list,
    )
    contact_appointment_date = MaybeListType(
        DateTimeType(),
        serialized_name="CPYCONTACTS_MEMBERSHIP_BeginningNominationDate",
        default=list,
    )
    contact_date_of_birth = MaybeListType(
        DateTimeType(), serialized_name="CPYCONTACTS_HEADER_Birthdate", default=list,
    )

    @property
    def address_fields(self):
        return [
            "address_line_one",
            "address_line_two",
            "address_line_three",
            "address_line_four",
            "postcode",
            "city",
            "country",
        ]

    @property
    def address_lines(self):
        return [
            line
            for line in (
                self.address_line_one,
                self.address_line_two,
                self.address_line_three,
                self.address_line_four,
            )
            if line is not None
        ]

    @property
    def freeform_address(self):
        return ", ".join(
            getattr(self, field)
            for field in self.address_fields
            if getattr(self, field) is not None
        )

    @property
    def num_contacts(self):
        return len(self.contact_bvd_id)

    def contact_merge_id(self, index):
        """ Generates a UUID to be used for merging contacts
        """
        if self.contact_uci[index]:
            return build_resolver_id(self.contact_uci[index])
        else:
            return build_resolver_id(self.contact_name[index])


class OwnershipData(Model):
    standardised_legal_form = StringType(
        serialized_name="STANDARDISED_LEGAL_FORM", default=None
    )

    shareholder_entity_type = ListType(
        StringType(), serialized_name="SH_ENTITY_TYPE", default=list, required=True
    )
    shareholder_bvd_id = ListType(
        StringType(), serialized_name="SH_BVD_ID_NUMBER", default=list, required=True
    )
    shareholder_bvd9 = ListType(StringType(), serialized_name="SH_BVD9", default=list)
    shareholder_uci = ListType(StringType(), serialized_name="SH_UCI", default=list)
    shareholder_lei = ListType(StringType(), serialized_name="SH_LEI", default=list)

    shareholder_country_code = ListType(
        StringType(), serialized_name="SH_COUNTRY_ISO_CODE", default=list
    )
    shareholder_state_province = ListType(
        StringType(), serialized_name="SH_STATE_PROVINCE", default=list
    )
    shareholder_state_province = ListType(
        StringType(), serialized_name="SH_STATE_PROVINCE", default=list
    )
    shareholder_name = ListType(StringType(), serialized_name="SH_NAME", default=list)
    shareholder_first_name = ListType(
        StringType(), serialized_name="SH_FIRST_NAME", default=list
    )
    shareholder_last_name = ListType(
        StringType(), serialized_name="SH_LAST_NAME", default=list
    )

    shareholder_direct_percentage = ListType(
        StringType(), serialized_name="SH_DIRECT_PCT", default=list
    )

    beneficial_owner_bvd_id = ListType(
        StringType(), serialized_name="BO_BVD_ID_NUMBER", default=list
    )
    beneficial_owner_uci = ListType(
        StringType(), serialized_name="BO_UCI", default=list
    )
    beneficial_owner_entity_type = ListType(
        StringType(), serialized_name="BO_ENTITY_TYPE", default=list
    )
    beneficial_owner_country_code = ListType(
        StringType(), serialized_name="BO_COUNTRY_ISO_CODE", default=list
    )
    beneficial_owner_name = ListType(
        StringType(), serialized_name="BO_NAME", default=list
    )
    beneficial_owner_first_name = ListType(
        StringType(), serialized_name="BO_FIRST_NAME", default=list
    )
    beneficial_owner_last_name = ListType(
        StringType(), serialized_name="BO_LAST_NAME", default=list
    )
    beneficial_owner_birth_date = ListType(
        DateTimeType(), serialized_name="BO_BIRTHDATE", default=list
    )

    @property
    def num_shareholders(self):
        return len(self.shareholder_bvd_id)

    @property
    def num_beneficial_owners(self):
        return len(self.beneficial_owner_bvd_id)

    def shareholder_is_individual(self, index):
        return (
            self.shareholder_entity_type[index]
            == "One or more named individuals or families"
        )

    def beneficial_owner_is_individual(self, index):
        return (
            self.beneficial_owner_entity_type[index]
            == "One or more named individuals or families"
        )

    def shareholder_merge_id(self, index):
        """ Generates a UUID to be used for merging shareholders
        """
        if self.shareholder_uci[index]:
            return build_resolver_id(self.shareholder_uci[index])
        else:
            return build_resolver_id(self.shareholder_name[index])

    def beneficial_owner_merge_id(self, index):
        """ Generates a UUID to be used for merging beneficial_owners
        """
        if self.beneficial_owner_uci[index]:
            return build_resolver_id(self.beneficial_owner_uci[index])
        else:
            return build_resolver_id(self.beneficial_owner_name[index])


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
    state = StringType(serialized_name="STATE", default=None)
    national_id = StringType(serialized_name="NATIONAL_ID", default=None)
    hint = StringType(serialized_name="HINT", default=None)
    score = FloatType(serialized_name="SCORE", default=None)


class WrappedMatch(Model):
    zero = ModelType(Match, serialized_name="0", required=True)


class SearchData(Model):
    bvd_id = StringType(serialized_name="BVDID", required=True)
    match = ModelType(WrappedMatch, serialized_name="MATCH", required=True)

    def score(self):
        if self.match.zero.hint == "Selected":
            return self.match.zero.score + 2
        elif self.match.zero.hint == "Potential":
            return self.match.zero.score + 1
        else:
            return self.match.zero.score


class DatabaseInfo(Model):
    version_number = StringType(serialized_name="VersionNumber")
    update_date = StringType(serialized_name="UpdateDate")
    update_number = StringType(serialized_name="UpdateNumber")
    release_number = StringType(serialized_name="ReleaseNumber")


class SearchSummary(Model):
    sort = DictType(StringType(), serialized_name="Sort")
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

    def merged_hits(a, b):
        return sorted(
            (a.data if a else []) + (b.data if b else []),
            reverse=True,
            key=lambda hit: hit.score()
        )

    def sorted_hits(self):
        return sorted(self.data, reverse=True, key=lambda hit: hit.score())


class Update(Model):
    bvd_id = StringType(serialized_name="BVD_ID_NUMBER", required=True)


class FetchUpdatesResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = MaybeListType(
        ModelType(Update), serialized_name="Data", default=list, required=True
    )


class CreateRecordSetResult(Model):
    comments = StringType(serialized_name="Comments")
    count = IntType(serialized_name="Count")
    id = UUIDType(serialized_name="Id")
    #    last_modified_utc = DateTimeType(serialized_name="LastModifiedUTC")
    name = StringType(serialized_name="Name")
    owner = BooleanType(serialized_name="Owner")
    shared = BooleanType(serialized_name="Shared")


class AddToRecordSetResult(Model):
    comments = StringType(serialized_name="Comments")
    count = IntType(serialized_name="Count")
    id = UUIDType(serialized_name="Id")
    #    last_modified_utc = DateTimeType(serialized_name="LastModifiedUTC")
    name = StringType(serialized_name="Name")
    owner = BooleanType(serialized_name="Owner")
    shared = BooleanType(serialized_name="Shared")
