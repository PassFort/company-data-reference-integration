import logging
from enum import Enum
import re

from pycountry import countries
from schematics import Model
from schematics.types import (
    FloatType,
    StringType,
    DateTimeType,
    DictType,
    ListType,
    IntType,
    BaseType,
    ModelType,
    BooleanType,
)

from app.passfort.base_model import BaseModel
from app.passfort.structured_company_type import StructuredCompanyType


def country_alpha_2_to_3(alpha_2):
    try:
        return countries.get(alpha_2=alpha_2).alpha_3
    except (LookupError, AttributeError):
        if alpha_2 != 'n.a.':
            logging.error(f"BvdD returned unrecognised alpha 2 country code {alpha_2}")
        return None


def name_strip(name: str) -> str:
    '''Clean names from useless garbage text'''
    garbage = ['via its funds']
    for string in garbage:
        if string in name:
            name = re.sub(string, '', name)
    return name


def format_names(first, last, full, entity_type):
    if first or last:
        return (
            name_strip(first) if first else '',
            name_strip(last) if last else ''
        )

    if full:
        full = name_strip(full)
        if entity_type == EntityType.INDIVIDUAL:
            names = full.split(' ')
            # First element is the title
            return ' '.join(names[1:-1]), names[-1]
        else:
            return '', full
    else:
        return '', ''


class ErrorCode(Enum):
    PROVIDER_UNKNOWN_ERROR = 303


class Error(BaseModel):
    source = StringType()
    code = IntType()
    message = StringType()
    info = BaseType()

    # TODO: What does this look like in other integrations
    def bad_response(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                "message": "Provider returned data in an unexpected format",
                "info": cause,
            }
        )


class EntityType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"


class TaxIdType(Enum):
    EUROVAT = "EUROVAT"
    VAT = "VAT"
    EIN = "EIN"


class TaxId(BaseModel):
    tax_id_type = StringType(required=True, choices=list(TaxIdType))
    value = StringType(required=True)


class OwnershipType(Enum):
    PARTNERSHIP = "PARTNERSHIP"
    COMPANY = "COMPANY"
    ASSOCIATION = "ASSOCIATION"
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    TRUST = "TRUST"
    OTHER = "OTHER"


class PreviousName(BaseModel):
    name = StringType(required=True)
    end = DateTimeType()

    def from_bvd(name, date):
        return PreviousName({"name": name, "end": date})


class SICCode(BaseModel):
    code = StringType(required=True)
    description = StringType(required=True)

    def from_bvd(primary_code, primary_label):
        return SICCode({"code": primary_code, "description": primary_label,})


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


class Shareholding(BaseModel):
    percentage = FloatType()

    def from_bvd(direct_percentage):
        try:
            return Shareholding({
                'percentage': float(direct_percentage) / 100
            })
        except ValueError:
            return None


class CompanyMetadata(BaseModel):
    bvd_id = StringType(required=True)
    number = ListType(StringType(), required=True)
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
                "structured_company_type": StructuredCompanyType.from_bvd(bvd_data.standardised_legal_form),
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
                        bvd_data.industry_primary_code, bvd_data.industry_primary_label,
                    )
                ],
                "contact_information": ContactDetails.from_bvd(bvd_data),
                "freeform_address": bvd_data.freeform_address,
                "is_active": next(
                    (status.lower().startswith("active") for status in bvd_data.status),
                    None,
                ),
                "is_active_details": next(iter(bvd_data.status), None),
                "trade_description": (
                    bvd_data.trade_description_english or bvd_data.trade_description_original_lang
                ),
                "description": bvd_data.products_services,
            }
        )


class Shareholder(BaseModel):
    type = StringType(required=True, choices=list(EntityType))
    bvd_id = StringType()
    bvd9 = StringType()
    bvd_uci = StringType()
    lei = StringType()
    country_of_incorporation = StringType(min_length=3, max_length=3)
    state_of_incorporation = StringType()
    first_names = StringType()
    last_name = StringType()
    shareholdings = ListType(ModelType(Shareholding))

    def from_bvd(index, bvd_data):
        entity_type = EntityType.INDIVIDUAL if bvd_data.shareholder_is_individual(index) else EntityType.COMPANY
        first_names, last_name = format_names(
            bvd_data.shareholder_first_name[index],
            bvd_data.shareholder_last_name[index],
            bvd_data.shareholder_name[index],
            entity_type,
        )

        return Shareholder(
            {
                "type": entity_type.value,
                "bvd_id": bvd_data.shareholder_bvd_id[index],
                "bvd9": bvd_data.shareholder_bvd9[index]
                if bvd_data.shareholder_bvd9
                else None,
                "bvd_uci": bvd_data.shareholder_uci[index],
                "lei": bvd_data.shareholder_lei[index],
                "country_of_incorporation": country_alpha_2_to_3(bvd_data.shareholder_country_code[index]),
                "state_of_incorporation": bvd_data.shareholder_state_province[index],
                "first_names": first_names,
                "last_name": last_name,
                "shareholdings": [
                    Shareholding.from_bvd(bvd_data.shareholder_direct_percentage[index])
                ]
                if bvd_data.shareholder_direct_percentage and bvd_data.shareholder_direct_percentage[index]
                else None,
            }
        )


class BeneficialOwner(BaseModel):
    type = StringType(required=True, choices=list(EntityType))
    bvd_id = StringType(required=True)
    bvd_uci = StringType(required=True)
    first_names = StringType()
    last_name = StringType()
    dob = DateTimeType()

    def from_bvd(index, bvd_data):
        uci = bvd_data.beneficial_owner_uci[index] if bvd_data.beneficial_owner_uci else None
        entity_type = EntityType.INDIVIDUAL if bvd_data.beneficial_owner_is_individual(index) else EntityType.COMPANY
        first_names, last_names = format_names(
            bvd_data.beneficial_owner_first_name[index],
            bvd_data.beneficial_owner_last_name[index],
            bvd_data.beneficial_owner_name[index],
            entity_type,
        )
        return BeneficialOwner({
            "type": entity_type.value,
            "bvd_id": bvd_data.beneficial_owner_bvd_id[index],
            "bvd_uci": uci,
            "first_names": first_names,
            "last_name": last_names,
            "dob": bvd_data.beneficial_owner_birth_date[index] if bvd_data.beneficial_owner_birth_date else None,
        })



class OwnershipStructure(BaseModel):
    shareholders = ListType(ModelType(Shareholder), required=True, default=list)
    beneficial_owners = ListType(
        ModelType(BeneficialOwner), required=True, default=list
    )

    def from_bvd(bvd_data):
        return OwnershipStructure(
            {
                "shareholders": [
                    Shareholder.from_bvd(i, bvd_data)
                    for i in range(0, len(bvd_data.shareholder_bvd_id))
                ],
                "beneficial_owners": [
                    BeneficialOwner.from_bvd(i, bvd_data)
                    for i in range(0, len(bvd_data.beneficial_owner_bvd_id))
                ],
            }
        )


class RegistryCompanyData(BaseModel):
    entity_type = StringType(required=True, choices=list(EntityType))
    metadata = ModelType(CompanyMetadata, required=True)

    def from_bvd(bvd_data):
        return RegistryCompanyData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": CompanyMetadata.from_bvd(bvd_data),
            }
        )


class OwnershipMetadata(BaseModel):
    company_type = StringType(required=True)
    structured_company_type = ModelType(StructuredCompanyType)

    def from_bvd(bvd_data):
        return OwnershipMetadata(
            {
                "company_type": bvd_data.standardised_legal_form,
                "structured_company_type": StructuredCompanyType.from_bvd(bvd_data.standardised_legal_form),
            }
        )


class OwnershipCompanyData(BaseModel):
    entity_type = StringType(choices=list(EntityType), required=True)
    metadata = ModelType(OwnershipMetadata, required=True)
    ownership_structure = ModelType(OwnershipStructure, required=True)

    def from_bvd(bvd_data):
        return OwnershipCompanyData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": OwnershipMetadata.from_bvd(bvd_data),
                "ownership_structure": OwnershipStructure.from_bvd(bvd_data),
            }
        )


class Credentials(BaseModel):
    key = StringType(required=True)


# TODO: ensure one of bvd_id and number is present
class RegistryInput(BaseModel):
    country_of_incorporation = StringType(min_length=3, max_length=3, required=True)
    bvd_id = StringType(default=None)
    number = StringType(default=None)


# TODO: ensure one of bvd_id and number is present
class OwnershipInput(BaseModel):
    country_of_incorporation = StringType(min_length=3, max_length=3, required=True)
    bvd_id = StringType(default=None)
    number = StringType(default=None)


class SearchInput(BaseModel):
    country = StringType(min_length=3, max_length=3, required=True)
    name = StringType(required=True)
    state = StringType(default=None)
    number = StringType(default=None)


class SearchRequest(BaseModel):
    credentials = ModelType(Credentials, required=True)
    input_data = ModelType(SearchInput, required=True)


class RegistryCheckRequest(BaseModel):
    credentials = ModelType(Credentials, required=True)
    input_data = ModelType(RegistryInput, required=True)


class OwnershipCheckRequest(BaseModel):
    credentials = ModelType(Credentials, required=True)
    input_data = ModelType(OwnershipInput, required=True)


class Candidate(BaseModel):
    bvd_id = StringType()
    bvd9 = StringType()
    name = StringType()
    number = StringType()
    country = StringType(min_length=3, max_length=3)
    status = StringType()

    def from_bvd(search_data):
        match_data = search_data.match.zero
        return Candidate({
            'bvd_id': search_data.bvd_id,
            'bvd9': match_data.bvd9,
            'name': match_data.name,
            'number': match_data.national_id,
            'country': country_alpha_2_to_3(match_data.country),
            'status': match_data.status,
        })


class SearchResponse(BaseModel):
    output_data = ListType(ModelType(Candidate))
    errors = ListType(ModelType(Error))
    raw = BaseType()


class RegistryCheckResponse(BaseModel):
    output_data = ModelType(RegistryCompanyData, serialize_when_none=True)
    errors = ListType(ModelType(Error), serialize_when_none=True, default=list)
    price = IntType()
    raw = BaseType()


class OwnershipCheckResponse(BaseModel):
    output_data = ModelType(OwnershipCompanyData, serialize_when_none=True)
    errors = ListType(ModelType(Error), serialize_when_none=True, default=list)
    price = IntType()
    raw = BaseType()
