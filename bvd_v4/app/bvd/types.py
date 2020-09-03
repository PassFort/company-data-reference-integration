from schematics import Model
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


class Data(Model):
    # Idenification
    bvd_id = StringType(serialized_name="BVD_ID_NUMBER", required=True)
    trade_register_number = StringType(serialized_name="TRADE_REGISTER_NUMBER")
    bvd9 = StringType(serialized_name="BVD9", required=True)
    name = StringType(serialized_name="NAME")
    previous_names = ListType(StringType(), serialized_name="PREVIOUS_NAME", required=True)
    previous_dates = ListType(DateTimeType(), serialized_name="PREVIOUS_NAME_DATE", required=True)
    isin = StringType(serialized_name="ISIN")
    lei = StringType(serialized_name="LEI", required=True)
    vat = StringType(serialized_name="VAT")
    eurovat = StringType(serialized_name="EUROVAT")
    irs = StringType(serialized_name="IRS")

    # Contact Details
    website = ListType(StringType(), serialized_name="WEBSITE")
    phone_number = ListType(StringType(), serialized_name="PHONE_NUMBER")
    email = ListType(StringType(), serialized_name="EMAIL")

    # Address
    address_type = StringType(serialized_name="ADDRESS_TYPE")
    address_line_one = StringType(serialized_name="ADDRESS_LINE1")
    address_line_two = StringType(serialized_name="ADDRESS_LINE2")
    address_line_three = StringType(serialized_name="ADDRESS_LINE3")
    address_line_four = StringType(serialized_name="ADDRESS_LINE4")
    postcode = StringType(serialized_name="POSTCODE")
    city = StringType(serialized_name="CITY")
    country_region = ListType(StringType(), serialized_name="COUNTRY_REGION")
    state = StringType(serialized_name="US_STATE")
    incorporation_state = StringType(serialized_name="INCORPORATION_STATE")
    country = StringType(serialized_name="COUNTRY")
    country_code = StringType(serialized_name="COUNTRY_ISO_CODE")
    longitude = FloatType(serialized_name="LONGITUDE")
    latitude = FloatType(serialized_name="LATITUDE")

    # Classification
    status = ListType(StringType(), serialized_name="STATUS")
    standardised_legal_form = StringType(serialized_name="STANDARDISED_LEGAL_FORM")
    products_services = StringType(serialized_name="PRODUCTS_SERVICES")
    trade_description_english = StringType(serialized_name="TRADE_DESCRIPTION_EN")
    trade_description_original_lang = StringType(
        serialized_name="TRADE_DESCRIPTION_ORIGINAL"
    )
    industry_classification = StringType(serialized_name="INDUSTRY_CLASSIFICATION")
    industry_primary_code = ListType(
        StringType(), serialized_name="INDUSTRY_PRIMARY_CODE"
    )
    industry_primary_label = ListType(
        StringType(), serialized_name="INDUSTRY_PRIMARY_LABEL"
    )
    industry_secondary_code = ListType(
        StringType(), serialized_name="INDUSTRY_SECONDARY_CODE"
    )
    industry_secondary_label = ListType(
        StringType(), serialized_name="INDUSTRY_SECONDARY_LABEL"
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


class SearchResult(Model):
    search_summary = ModelType(SearchSummary, serialized_name="SearchSummary")
    data = ListType(ModelType(Data), serialized_name="Data")
