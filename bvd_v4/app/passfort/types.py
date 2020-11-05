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
    DateTimeType,
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
        if alpha_2 != "n.a." and alpha_2 != "-" and alpha_2 is not None:
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

    def get_country_code(name):
        try:
            country = countries.lookup(name)
            return country.alpha_3
        except (LookupError, AttributeError):
            return None

    def get_possible_names(country_name):
        # BvD can return names that don't match pycountry fields
        name_mapping = {"Korea Republic of": "Korea, Republic of"}

        names = []
        name = country_name.split(";")[0]
        names.append(name)
        names.append(name.split(",")[0])
        names.append(name_mapping.get(name))
        return names

    possible_names = get_possible_names(country_name)
    for n in possible_names:
        country_code = get_country_code(n)
        if country_code:
            break

    if not country_code:
        logging.error(
            {
                "error": "BvD returned unrecognised country name",
                "info": {"country_name": country_name,},
            }
        )
    return country_code


def name_strip(name: str) -> str:
    """Clean names from useless garbage text"""
    garbage = ["via its funds"]
    for string in garbage:
        if string in name:
            name = re.sub(string, "", name)
    return name


def format_names(first, last, full, entity_type):
    if not first and not last:
        if full:
            full = name_strip(full)
            names = full.split(" ")
            # First element is the title
            return names[0], names[1:-1], names[-1]
        else:
            return None, [], ""
    else:
        names_from_full = (
            [name for name in name_strip(full).split(" ") if name] if full else []
        )
        names_from_first = (
            [name for name in name_strip(first).split(" ") if name] if first else []
        )
        first_name = names_from_first[0] if names_from_first else None
        possible_title = names_from_full[0] if names_from_full else None
        return (
            possible_title if possible_title != first_name else None,
            names_from_first,
            name_strip(last) if last else "",
        )


class ErrorCode(Enum):
    PROVIDER_CONNECTION_ERROR = 302
    PROVIDER_UNKNOWN_ERROR = 303
    PROVIDER_MISCONFIGURATION_ERROR = 205

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
                "info": {"raw": cause},
            }
        )

    def bad_provider_response(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_UNKNOWN_ERROR.value,
                "message": "Provider returned data in an unexpected format",
                "info": {"raw": cause},
            }
        )

    def provider_connection(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_CONNECTION_ERROR.value,
                "message": "Failed to connect to provider",
                "info": {"raw": cause},
            }
        )

    def provider_rate_limit_exceeded(cause):
        return Error(
            {
                "source": "PROVIDER",
                "code": ErrorCode.PROVIDER_CONNECTION_ERROR.value,
                "message": "Provider rate limit exceeded",
                "info": {"raw": cause},
            }
        )

    def provider_bad_credentials(cause):
        return Error({
            'code': ErrorCode.PROVIDER_MISCONFIGURATION_ERROR.value,
            'source': 'PROVIDER',
            'message': 'Failed to authenticate with the provider. Please check your credentials.',
            "info": {"raw": cause},
        })


class EntityType(Enum):
    INDIVIDUAL = "INDIVIDUAL"
    COMPANY = "COMPANY"

    def from_bvd_officer(index, bvd_data):
        bvd_type = bvd_data.contact_entity_type[index]
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

    def from_bvd_us_sic(bvd_data):
        return [
            IndustryClassification({
                "code": code,
                "description": label,
                "classification_version": "US SIC",
                "classification_type": IndustryClassificationType.SIC.value
            }) for code, label in zip(
                bvd_data.us_sic_core_code,
                bvd_data.us_sic_core_label,
            )
        ]

    def from_bvd_nace(bvd_data):
        return [
            IndustryClassification({
                "code": code,
                "description": label,
                "classification_version": "NACE Rev. 2",
                "classification_type": IndustryClassificationType.NACE.value,
            }) for code, label in zip(
                bvd_data.nace2_core_code,
                bvd_data.nace2_core_label,
            )
        ]

    def from_bvd_naics(bvd_data):
        return [
            IndustryClassification({
                "code": code,
                "description": label,
                "classification_version": "NAICS 2017",
                "classification_type": IndustryClassificationType.NAICS.value,
            }) for code, label in zip(
                bvd_data.naics2017_core_code,
                bvd_data.naics2017_core_label,
            )
        ]

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
            return Shareholding({"percentage": percentage})
        except InvalidOperation:
            logging.warning(
                {
                    "error": "BvD returned invalid share percentage",
                    "info": {"percentage": direct_percentage},
                }
            )


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
        return "STRUCTURED"

    def from_bvd(bvd_data):
        return StructuredAddress(
            {
                "postal_code": bvd_data.postcode,
                "route": bvd_data.address_line_one,
                "locality": bvd_data.city,
                "state_province": bvd_data.state,
                "country": country_alpha_2_to_3(bvd_data.country_code),
                "address_lines": bvd_data.address_lines,
                "original_freeform_address": bvd_data.freeform_address,
            }
        )


class CompanyAddress(BaseModel):
    type_ = StringType(choices=["registered_address"], serialized_name="type")
    address = ModelType(StructuredAddress)

    def from_bvd(bvd_data):
        return CompanyAddress(
            {
                "type": "registered_address",
                "address": StructuredAddress.from_bvd(bvd_data),
            }
        )


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
                ]
                + [TaxId.from_bvd_vat(tax_id) for tax_id in bvd_data.vat],
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
                "industry_classifications": 
                    IndustryClassification.from_bvd_us_sic(bvd_data) +
                    IndustryClassification.from_bvd_nace(bvd_data) +
                    IndustryClassification.from_bvd_naics(bvd_data),
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


class Credentials(BaseModel):
    key = StringType(required=True)


# TODO: ensure one of bvd_id and number is present
class RegistryInput(BaseModel):
    country_of_incorporation = StringType(min_length=3, max_length=3, required=True)
    bvd_id = StringType(default=None)
    number = StringType(default=None)
    name = StringType(default=None)
    state_of_incorporation = StringType(default=None)


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



class Portfolio(BaseModel):
    id = UUIDType(required=True)
    count = IntType()


class PortfolioItem(BaseModel):
    bvd_id = StringType(required=True)
    portfolio_id = StringType(required=True)


class NewPortfolio(BaseModel):
    name = StringType()


class TimeFrame(BaseModel):
    from_ = DateTimeType(serialized_name="from", required=True)
    to = DateTimeType(required=True)


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
    end_date = DateTimeType(required=True)
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


class CreatePortfolioResponse(Request):
    output_data = ModelType(Portfolio, required=True)


class AddToPortfolioResponse(Request):
    output_data = ModelType(Portfolio, required=True)
