from enum import Enum

from schematics import Model
from schematics.types import (
    FloatType,
    StringType,
    DateTimeType,
    ListType,
    IntType,
    BaseType,
    ModelType,
    BooleanType,
)


class BaseModel(Model):
    class Options:
        serialize_when_none = False


class TaxIdType(Enum):
    EUROVAT = "EUROVAT"
    VAT = "VAT"
    EIN = "EIN"


class TaxId(BaseModel):
    tax_id_type = StringType(required=True, choices=[ty for ty in TaxIdType])
    value = StringType(required=True)


class OwnershipType(Enum):
    PARTNERSHIP = "PARTNERSHIP"
    COMPANY = "COMPANY"
    ASSOCIATION = "ASSOCIATION"
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    TRUST = "TRUST"
    OTHER = "OTHER"


class StructuredCompanyType(BaseModel):
    ownership_type = StringType(choices=[ty for ty in OwnershipType])
    is_public = BooleanType()
    is_limit = BooleanType()


class PreviousName(BaseModel):
    name = StringType(required=True)
    end = DateTimeType()

    def from_bvd(name, date):
        return PreviousName({"name": name, "end": date})


class SICCode(BaseModel):
    code = StringType(required=True)
    description = StringType(required=True)

    def from_bvd(primary_code, primary_label):
        return SICCode({
            'code': primary_code,
            'description': primary_label,
        })


class ContactDetails(BaseModel):
    url = StringType()
    phone_number = StringType()
    email = StringType()

    def from_bvd(bvd_data):
        return ContactDetails({
            'url': next(iter(bvd_data.website), None),
            'phone_number': next(iter(bvd_data.phone_number), None),
            'email': next(iter(bvd_data.email), None),
        })


class CompanyMetadata(BaseModel):
    bvd_id = StringType(required=True)
    number = StringType(required=True)
    bvd9 = StringType(required=True)
    isin = StringType()
    lei = StringType(required=True)
    tax_ids = ListType(ModelType(TaxId), required=True)
    name = StringType()
    company_type = StringType()
    structured_company_type = ModelType(StructuredCompanyType)
    country_of_incorporation = StringType()
    incorporation_date = DateTimeType()
    previous_names = ListType(ModelType(PreviousName), required=True)
    sic_codes = ListType(ModelType(SICCode), required=True)
    contact_information = ModelType(ContactDetails)
    freeform_address = StringType(required=True)
    is_active = BooleanType()
    is_active_details = StringType()
    trade_description = StringType()
    description = StringType()

    def from_bvd(bvd_data):
        return CompanyMetadata(
            {
                "bvd_id": bvd_data.bvd_id,
                "number": bvd_data.trade_register_number,
                "bvd9": bvd_data.bvd9,
                "isin": bvd_data.isin,
                "lei": bvd_data.lei,
                "name": bvd_data.name,
                "company_type": bvd_data.standardised_legal_form,
                "structured_company_type": None,
                "country_of_incorporation": None,
                "incorporation_date": None,
                "previous_names": [
                    PreviousName.from_bvd(name, date)
                    for name, date in zip(
                        bvd_data.previous_names, bvd_data.previous_dates
                    )
                ],
                "sic_codes": [
                    # TODO: deeper SIC code support
                    SICCode.from_bvd(primary_code, primary_label)
                    for primary_code, primary_label in zip(
                        bvd_data.industry_primary_code,
                        bvd_data.industry_primary_label,
                    )
                ],
                "contact_information": ContactDetails.from_bvd(bvd_data),
                "freeform_address": bvd_data.freeform_address,
                "is_active": next((
                    status.lower().startswith('active')
                    for status
                    in bvd_data.status
                ), None),
                "is_active_details": next(iter(bvd_data.status), None),
                "trade_description": bvd_data.trade_description_english or bvd_data.trade_description_original_lang,
                "description": bvd_data.products_services,
            }
        )


class EntityType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class CompanyData(BaseModel):
    entity_type = StringType(required=True, choices=[ty for ty in EntityType])
    metadata = ModelType(CompanyMetadata, required=True)
    #    officers: Officers

    def from_bvd(bvd_data):
        return CompanyData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": CompanyMetadata.from_bvd(bvd_data),
            }
        )


class Credentials(Model):
    key = StringType(required=True)


class RegistryInput(Model):
    country_of_incorporation = StringType(min_length=3, max_length=3, required=True)
    number = StringType(required=True)


class RegistryCheckRequest(Model):
    input_data = ModelType(RegistryInput)
    credentials = ModelType(Credentials)
