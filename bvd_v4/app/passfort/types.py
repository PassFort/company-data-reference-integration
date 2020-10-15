import logging
from decimal import Decimal, InvalidOperation
from enum import Enum
import re

from pycountry import countries
from schematics import Model
from schematics.types import (
    BooleanType,
    DecimalType,
    FloatType,
    StringType,
    DateType,
    DictType,
    ListType,
    IntType,
    BaseType,
    ModelType,
    UUIDType,
)
from schematics.types.serializable import serializable

from app.constants import PROVIDER_NAME
from app.passfort.base_model import BaseModel
from app.passfort.structured_company_type import StructuredCompanyType


def country_alpha_2_to_3(alpha_2):
    try:
        return countries.get(alpha_2=alpha_2).alpha_3
    except (LookupError, AttributeError):
        if alpha_2 != "n.a." and alpha_2 is not None:
            logging.error(
                {
                    "error": "BvD returned unrecognised alpha 2 country code",
                    "info": {"alpha_2": alpha_2},
                }
            )
        return None


def country_names_to_alpha_3(country_name):
    if country_name is None:
        return None

    try:
        return countries.get(name=country_name.split(";")[0]).alpha_3
    except (LookupError, AttributeError):
        logging.error(
            {
                "error": "BvD returned unrecognised country name",
                "info": {"country_name": country_name,},
            }
        )
        return None


def name_strip(name: str) -> str:
    """Clean names from useless garbage text"""
    garbage = ["via its funds"]
    for string in garbage:
        if string in name:
            name = re.sub(string, "", name)
    return name


def format_names(first, last, full, entity_type):
    if full:
        full = name_strip(full)
        if entity_type == EntityType.INDIVIDUAL:
            names = full.split(" ")
            # First element is the title
            return names[0], names[1:-1], names[-1]
        else:
            return None, [], full
    elif first or last:
        return (
            None,
            name_strip(first) if first else [],
            name_strip(last) if last else "",
        )
    else:
        return None, [], ""


class ErrorCode(Enum):
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303


class Error(BaseModel):
    source = StringType()
    code = IntType()
    message = StringType()
    info = BaseType()

    def provider_unknown_error(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                "message": "Unknown provider error",
                "info": cause,
            }
        )

    def bad_provider_response(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                "message": "Provider returned data in an unexpected format",
                "info": cause,
            }
        )

    def provider_connection(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_CONNECTION_ERROR.value,
                "message": "Failed to connect to provider",
                "info": cause,
            }
        )


class EntityType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"

    def from_bvd_officer(index, bvd_data):
        bvd_type = bvd_data.officer_entity_type[index]
        if "Individual" == bvd_type:
            return EntityType.INDIVIDUAL
        elif "Company" == bvd_type:
            return EntityType.COMPANY
        else:
            return None


class TaxIdType(Enum):
    EUROVAT = "EUROVAT"
    VAT = "VAT"
    EIN = "EIN"


class TaxId(BaseModel):
    tax_id_type = StringType(choices=[ty.value for ty in TaxIdType], required=True)
    value = StringType(required=True)

    def from_bvd_vat(bvd_vat):
        return TaxId({"tax_id_type": TaxIdType.VAT.value, "value": bvd_vat})

    def from_bvd_eurovat(bvd_eurovat):
        return TaxId({"tax_id_type": TaxIdType.EUROVAT.value, "value": bvd_eurovat})


class OwnershipType(Enum):
    PARTNERSHIP = "PARTNERSHIP"
    COMPANY = "COMPANY"
    ASSOCIATION = "ASSOCIATION"
    SOLE_PROPRIETORSHIP = "SOLE_PROPRIETORSHIP"
    TRUST = "TRUST"
    OTHER = "OTHER"


class PreviousName(BaseModel):
    name = StringType(required=True)
    end = DateType()

    def from_bvd(name, date):
        return PreviousName({"name": name, "end": date})


class IndustryClassificationType(Enum):
    SIC = "SIC"
    NACE = "NACE"
    NAICS = "NAICS"
    OTHER = "OTHER"

    def from_bvd(bvd_classification):
        if "SIC" in bvd_classification:
            return IndustryClassificationType.SIC
        elif "NACE" in bvd_classification:
            return IndustryClassificationType.NACE
        elif "NAICS" in bvd_classification:
            return IndustryClassificationType.NAICS
        else:
            logging.warning(
                {
                    "error": "Unrecognised industry classification",
                    "info": {"classification": bvd_classification,},
                }
            )
            return IndustryClassificationType.OTHER


class IndustryClassification(BaseModel):
    classification_type = StringType(
        choices=[ty.value for ty in IndustryClassificationType], required=True
    )
    code = StringType(required=True)
    classification_version = StringType()
    description = StringType()


class SICCode(BaseModel):
    code = StringType(required=True)
    description = StringType(required=True)

    def from_bvd(primary_code, primary_label):
        return SICCode({"code": primary_code, "description": primary_label})


class ContactDetails(BaseModel):
    url = StringType()
    phone_number = StringType()
    email = StringType()

    def from_bvd(bvd_data):
        return ContactDetails(
            {
                "url": next(iter(bvd_data.website), None),
                "phone_number": next(iter(bvd_data.phone_number), None),
                "email": next(iter(bvd_data.email), None),
            }
        )


class Shareholding(BaseModel):
    percentage = FloatType()

    @serializable
    def provider_name(self):
        return PROVIDER_NAME

    def from_bvd(direct_percentage):
        if direct_percentage is None:
            return None

        try:
            percentage = Decimal(direct_percentage)
            return Shareholding({"percentage": percentage / 100})
        except InvalidOperation:
            logging.warning({
                "error": "BvD returned invalid share percentage",
                "info": {"percentage": direct_percentage},
            })


class StructuredAddress(BaseModel):
    postal_code = StringType()
    route = StringType()
    locality = StringType()
    state_province = StringType()
    country = StringType(min_length=3, max_length=3)
    address_lines = ListType(StringType())
    original_freeform_address = StringType()

    @serializable
    def type(self):
        return 'STRUCTURED'

    def from_bvd(bvd_data):
        return StructuredAddress({
            "postal_code": bvd_data.postcode,
            "route": bvd_data.address_line_one,
            "locality": bvd_data.city,
            "state_province": bvd_data.state,
            "country": country_names_to_alpha_3(bvd_data.country),
            "address_lines": bvd_data.address_lines,
            "original_freeform_address": bvd_data.freeform_address,
        })


class CompanyAddress(BaseModel):
    type_ = StringType(choices=["registered_address"], serialized_name="type")
    address = ModelType(StructuredAddress)

    def from_bvd(bvd_data):
        return CompanyAddress({
            "type": "registered_address",
            "address": StructuredAddress.from_bvd(bvd_data)
        })


class CompanyMetadata(BaseModel):
    bvd_id = StringType()
    number = StringType()
    bvd9 = StringType()
    isin = StringType()
    lei = StringType()
    tax_ids = ListType(ModelType(TaxId), default=list, required=True)
    name = StringType()
    company_type = StringType()
    structured_company_type = ModelType(StructuredCompanyType)
    country_of_incorporation = StringType()
    incorporation_date = DateType()
    previous_names = ListType(ModelType(PreviousName), required=True)
    industry_classifications = ListType(ModelType(IndustryClassification))
    sic_codes = ListType(ModelType(SICCode), required=True)
    contact_information = ModelType(ContactDetails)
    addresses = ListType(ModelType(CompanyAddress), default=list, required=True)
    is_active = BooleanType()
    is_active_details = StringType()
    trade_description = StringType()
    description = StringType()

    def from_bvd(bvd_data):
        return CompanyMetadata(
            {
                "bvd_id": bvd_data.bvd_id,
                "number": bvd_data.trade_register_number[0]
                if bvd_data.trade_register_number
                else None,
                "bvd9": bvd_data.bvd9,
                "isin": bvd_data.isin,
                "lei": bvd_data.lei,
                "tax_ids": [
                    TaxId.from_bvd_eurovat(tax_id) for tax_id in bvd_data.eurovat
                ] + [
                    TaxId.from_bvd_vat(tax_id) for tax_id in bvd_data.vat
                ],
                "name": bvd_data.name,
                "company_type": bvd_data.standardised_legal_form,
                "structured_company_type": StructuredCompanyType.from_bvd(
                    bvd_data.standardised_legal_form
                ),
                "country_of_incorporation": country_alpha_2_to_3(bvd_data.country_code),
                "incorporation_date": bvd_data.incorporation_date,
                "previous_names": [
                    PreviousName.from_bvd(name, date)
                    for name, date in zip(
                        bvd_data.previous_names, bvd_data.previous_dates
                    )
                ],
                "industry_classifications": [
                    IndustryClassification(
                        {
                            "classification_type": IndustryClassificationType.from_bvd(
                                bvd_data.industry_classification
                            ).value,
                            "classification_version": bvd_data.industry_classification,
                            "code": primary_code,
                            "description": primary_label,
                        }
                    )
                    for primary_code, primary_label in zip(
                        bvd_data.industry_primary_code, bvd_data.industry_primary_label,
                    )
                ],
                "sic_codes": [
                    SICCode.from_bvd(primary_code, primary_label)
                    for primary_code, primary_label in zip(
                        bvd_data.industry_primary_code, bvd_data.industry_primary_label,
                    )
                ],
                "contact_information": ContactDetails.from_bvd(bvd_data),
                "addresses": [CompanyAddress.from_bvd(bvd_data)],
                "is_active": next(
                    (status.lower().startswith("active") for status in bvd_data.status),
                    None,
                ),
                "is_active_details": next(iter(bvd_data.status), None),
                "trade_description": (
                    bvd_data.trade_description_english
                    or bvd_data.trade_description_original_lang
                ),
                "description": bvd_data.products_services,
            }
        )


class Shareholder(BaseModel):
    type = StringType(required=True, choices=[ty.value for ty in EntityType])
    bvd_id = StringType()
    bvd9 = StringType()
    bvd_uci = StringType()
    lei = StringType()
    country_of_incorporation = StringType(min_length=3, max_length=3)
    state_of_incorporation = StringType()
    first_names = StringType()
    last_name = StringType()
    shareholdings = ListType(ModelType(Shareholding))

    def from_bvd_shareholder(index, bvd_data):
        entity_type = (
            EntityType.INDIVIDUAL
            if bvd_data.shareholder_is_individual(index)
            else EntityType.COMPANY
        )
        title, first_names, last_name = format_names(
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
                "country_of_incorporation": country_alpha_2_to_3(
                    bvd_data.shareholder_country_code[index]
                ),
                "state_of_incorporation": bvd_data.shareholder_state_province[index],
                "first_names": "".join(first_names),
                "last_name": last_name,
                "shareholdings": [
                    Shareholding.from_bvd(bvd_data.shareholder_direct_percentage[index])
                ]
                if bvd_data.shareholder_direct_percentage
                and bvd_data.shareholder_direct_percentage[index]
                else None,
            }
        )


class BeneficialOwner(BaseModel):
    type = StringType(required=True, choices=[ty.value for ty in EntityType])
    bvd_id = StringType(required=True)
    bvd_uci = StringType(required=True)
    first_names = StringType()
    last_name = StringType()
    dob = DateType()

    def from_bvd_beneficial_owner(index, bvd_data):
        uci = (
            bvd_data.beneficial_owner_uci[index]
            if bvd_data.beneficial_owner_uci
            else None
        )
        entity_type = (
            EntityType.INDIVIDUAL
            if bvd_data.beneficial_owner_is_individual(index)
            else EntityType.COMPANY
        )
        title, first_names, last_names = format_names(
            bvd_data.beneficial_owner_first_name[index],
            bvd_data.beneficial_owner_last_name[index],
            bvd_data.beneficial_owner_name[index],
            entity_type,
        )
        return BeneficialOwner(
            {
                "type": entity_type.value,
                "bvd_id": bvd_data.beneficial_owner_bvd_id[index],
                "bvd_uci": uci,
                "first_names": "".join(first_names),
                "last_name": last_names,
                "dob": bvd_data.beneficial_owner_birth_date[index]
                if bvd_data.beneficial_owner_birth_date
                else None,
            }
        )


class OwnershipStructure(BaseModel):
    shareholders = ListType(ModelType(Shareholder), required=True, default=list)
    beneficial_owners = ListType(
        ModelType(BeneficialOwner), required=True, default=list
    )

    def from_bvd(bvd_data):
        return OwnershipStructure(
            {
                "shareholders": [
                    Shareholder.from_bvd_shareholder(i, bvd_data)
                    for i in range(0, len(bvd_data.shareholder_bvd_id))
                ],
                "beneficial_owners": [
                    BeneficialOwner.from_bvd_beneficial_owner(i, bvd_data)
                    for i in range(0, len(bvd_data.beneficial_owner_bvd_id))
                ],
            }
        )


class OfficerRole(Enum):
    INDIVIDUAL_DIRECTOR = "INDIVIDUAL_DIRECTOR"
    INDIVIDUAL_COMPANY_SECRETARY = "INDIVIDUAL_COMPANY_SECRETARY"
    INDIVIDUAL_OTHER = "INDIVIDUAL_OTHER"
    COMPANY_DIRECTOR = "COMPANY_DIRECTOR"
    COMPANY_COMPANY_SECRETARY = "COMPANY_COMPANY_SECRETARY"
    COMPANY_OTHER = "COMPANY_OTHER"

    def director(entity_type):
        if entity_type is EntityType.INDIVIDUAL:
            return OfficerRole.INDIVIDUAL_DIRECTOR
        else:
            return OfficerRole.COMPANY_DIRECTOR

    def secretary(entity_type):
        if entity_type is EntityType.INDIVIDUAL:
            return OfficerRole.INDIVIDUAL_COMPANY_SECRETARY
        else:
            return OfficerRole.COMPANY_COMPANY_SECRETARY

    def other(entity_type):
        if entity_type is EntityType.INDIVIDUAL:
            return OfficerRole.INDIVIDUAL_OTHER
        else:
            return OfficerRole.COMPANY_OTHER

    def from_bvd_officer(index, bvd_data):
        original_role_lower = bvd_data.officer_role[index].lower()
        entity_type = EntityType.from_bvd_officer(index, bvd_data)

        if "director" in original_role_lower:
            return OfficerRole.director(entity_type)
        elif "secretary" in original_role_lower:
            return OfficerRole.secretary(entity_type)
        else:
            return OfficerRole.other(entity_type)


class Officer(BaseModel):
    bvd_id = StringType()
    bvd_uci = StringType()
    type = StringType(required=True, choices=[ty.value for ty in EntityType])
    role = StringType(required=True, choices=[role.value for role in OfficerRole])
    original_role = StringType()
    first_names = StringType()
    last_name = StringType()
    nationality = StringType(min_length=3, max_length=3)
    resigned = BooleanType()
    resigned_on = DateType()
    appointed_on = DateType()
    dob = DateType()

    def from_bvd_officer(index, bvd_data):
        entity_type = EntityType.from_bvd_officer(index, bvd_data)
        officer_role = OfficerRole.from_bvd_officer(index, bvd_data)

        _, first_names, last_name = format_names(
            " ".join(
                [
                    bvd_data.officer_first_name[index] or "",
                    bvd_data.officer_middle_name[index] or "",
                ]
            ),
            bvd_data.officer_last_name[index],
            bvd_data.officer_name[index],
            entity_type,
        )

        return Officer(
            {
                "bvd_id": bvd_data.officer_bvd_id[index],
                "bvd_uci": bvd_data.officer_uci[index],
                "type": entity_type.value if entity_type else None,
                "role": officer_role.value if officer_role else None,
                "original_role": bvd_data.officer_role[index],
                "first_names": " ".join(first_names),
                "last_name": last_name,
                "nationality": country_names_to_alpha_3(
                    bvd_data.officer_nationality[index]
                ),
                "resigned": bvd_data.officer_current_previous[index] == "Previous",
                "resigned_on": bvd_data.officer_resignation_date[index],
                "appointed_on": bvd_data.officer_appointment_date[index],
                "dob": bvd_data.officer_date_of_birth[index],
            }
        )

    @property
    def is_director(self):
        return "DIRECTOR" in self.role

    @property
    def is_secretary(self):
        return "SECRETARY" in self.role


class Officers(BaseModel):
    directors = ListType(ModelType(Officer), default=list, required=True)
    secretaries = ListType(ModelType(Officer), default=list, required=True)
    resigned = ListType(ModelType(Officer), default=list, required=True)
    others = ListType(ModelType(Officer), default=list, required=True)

    def from_bvd(bvd_data):
        officers = [
            Officer.from_bvd_officer(index, bvd_data)
            for index in range(0, len(bvd_data.officer_bvd_id))
        ]
        return Officers(
            {
                "directors": [
                    officer
                    for officer in officers
                    if officer.is_director and not officer.resigned
                ],
                "secretaries": [
                    officer
                    for officer in officers
                    if officer.is_secretary and not officer.resigned
                ],
                "resigned": [officer for officer in officers if officer.resigned],
                "others": [
                    officer
                    for officer in officers
                    if not any(
                        [officer.is_director, officer.is_secretary, officer.resigned]
                    )
                ],
            }
        )


class RegistryCompanyData(BaseModel):
    entity_type = StringType(required=True, choices=[ty.value for ty in EntityType])
    metadata = ModelType(CompanyMetadata, required=True)
    officers = ModelType(Officers, required=True)

    def from_bvd(bvd_data):
        return RegistryCompanyData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": CompanyMetadata.from_bvd(bvd_data),
                "officers": Officers.from_bvd(bvd_data),
            }
        )


class OwnershipMetadata(BaseModel):
    company_type = StringType(required=True)
    structured_company_type = ModelType(StructuredCompanyType)

    def from_bvd(bvd_data):
        return OwnershipMetadata(
            {
                "company_type": bvd_data.standardised_legal_form,
                "structured_company_type": StructuredCompanyType.from_bvd(
                    bvd_data.standardised_legal_form
                ),
            }
        )


class OwnershipCompanyData(BaseModel):
    entity_type = StringType(choices=[ty.value for ty in EntityType], required=True)
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
    name = StringType(default=None)


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


class Request(BaseModel):
    credentials = ModelType(Credentials, required=True)
    is_demo = BooleanType(default=False)


class SearchRequest(Request):
    input_data = ModelType(SearchInput, required=True)


class RegistryCheckRequest(Request):
    input_data = ModelType(RegistryInput, required=True)


class OwnershipCheckRequest(Request):
    input_data = ModelType(OwnershipInput, required=True)


class Portfolio(BaseModel):
    id = UUIDType(required=True)
    count = IntType()


class PortfolioItem(BaseModel):
    bvd_id = StringType(required=True)
    portfolio_id = StringType(required=True)


class NewPortfolio(BaseModel):
    name = StringType()


class TimeFrame(BaseModel):
    from_ = DateType(serialized_name="from", required=True)
    to = DateType(required=True)


class EventsInput(BaseModel):
    callback_url = StringType(required=True)
    portfolio_name = StringType(required=True)
    portfolio_id = UUIDType(required=True)
    timeframe = ModelType(TimeFrame, required=True)


class CreatePortfolioRequest(Request):
    input_data = ModelType(NewPortfolio, required=True)


class AddToPortfolioRequest(Request):
    input_data = ModelType(PortfolioItem, required=True)


class MonitoringEventsRequest(Request):
    input_data = ModelType(EventsInput, required=True)


class EventType(Enum):
    VERIFY_COMPANY_DETAILS = "verify_company_details"
    IDENTIFY_SHAREHOLDERS = "identify_shareholders"
    IDENTIFY_OFFICERS = "identify_officers"


class Event(BaseModel):
    bvd_id = StringType(required=True)
    event_type = StringType(choices=[ty.value for ty in EventType], required=True)


class RegistryEvent(Event):
    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("event_type") == EventType.VERIFY_COMPANY_DETAILS.value

    def from_bvd_update(update):
        return RegistryEvent(
            {
                "bvd_id": update.bvd_id,
                "event_type": EventType.VERIFY_COMPANY_DETAILS.value,
            }
        )


class ShareholdersEvent(Event):
    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("event_type") == EventType.IDENTIFY_SHAREHOLDERS.value

    def from_bvd_update(update):
        return ShareholdersEvent(
            {
                "bvd_id": update.bvd_id,
                "event_type": EventType.IDENTIFY_SHAREHOLDERS.value,
            }
        )


class OfficersEvent(Event):
    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("event_type") == EventType.IDENTIFY_OFFICERS.value

    def from_bvd_update(update):
        return OfficersEvent(
            {"bvd_id": update.bvd_id, "event_type": EventType.IDENTIFY_OFFICERS.value}
        )


class EventsCallback(BaseModel):
    portfolio_id = UUIDType(required=True)
    portfolio_name = StringType(required=True)
    events = ListType(ModelType(Event), required=True)
    raw = BaseType()


class Candidate(BaseModel):
    bvd_id = StringType()
    bvd9 = StringType()
    name = StringType()
    number = StringType()
    country = StringType(min_length=3, max_length=3)
    status = StringType()

    def from_bvd(search_data):
        match_data = search_data.match.zero
        return Candidate(
            {
                "bvd_id": search_data.bvd_id,
                "bvd9": match_data.bvd9,
                "name": match_data.name,
                "number": match_data.national_id,
                "country": country_alpha_2_to_3(match_data.country),
                "status": match_data.status,
            }
        )


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


class CreatePortfolioResponse(Request):
    output_data = ModelType(Portfolio, required=True)


class AddToPortfolioResponse(Request):
    output_data = ModelType(Portfolio, required=True)
