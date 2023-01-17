from typing import List, Optional

from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import (
    BaseType,
    BooleanType,
    DateType,
    DictType,
    FloatType,
    IntType,
    ListType,
    ModelType,
    PolyModelType,
    StringType,
    UUIDType,
)
from schematics.types.base import TypeMeta


class BaseModel(Model):
    class Options:
        export_level = NOT_NONE


# Inheriting this class will make an enum exhaustive
class EnumMeta(TypeMeta):
    def __new__(mcs, name, bases, attrs):
        attrs["choices"] = [
            v for k, v in attrs.items() if not k.startswith("_") and k.isupper()
        ]
        return TypeMeta.__new__(mcs, name, bases, attrs)


class ApproxDateType(DateType):
    formats = ["%Y-%m"]


# Intentionally non-exhaustive
class DemoResultType(StringType):
    ANY = "ANY"
    ANY_CHARGE = "ANY_CHARGE"
    NO_MATCH = "NO_MATCH"

    # Errors
    ERROR_INVALID_CREDENTIALS = "ERROR_INVALID_CREDENTIALS"
    ERROR_ANY_PROVIDER_MESSAGE = "ERROR_ANY_PROVIDER_MESSAGE"
    ERROR_CONNECTION_TO_PROVIDER = "ERROR_CONNECTION_TO_PROVIDER"

    # Company search specific
    NO_HITS = "NO_HITS"
    MANY_HITS = "MANY_HITS"

    # Company data check specific
    NO_DATA = "NO_DATA"
    ALL_DATA = "ALL_DATA"
    COMPANY_INACTIVE = "COMPANY_INACTIVE"
    COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH = (
        "COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH"
    )
    COMPANY_NAME_MISMATCH = "COMPANY_NAME_MISMATCH"
    COMPANY_NUMBER_MISMATCH = "COMPANY_NUMBER_MISMATCH"
    COMPANY_ADDRESS_MISMATCH = "COMPANY_ADDRESS_MISMATCH"
    COMPANY_ADDRESS_MATCH = "COMPANY_ADDRESS_MATCH"
    # Associates data
    COMPANY_RESGINED_OFFICER = "COMPANY_RESIGNED_OFFICER"
    COMPANY_FORMER_SHAREHOLDER = "COMPANY_FORMER_SHAREHOLDER"
    COMPANY_OFFICER_WITH_MULTIPLE_ROLES = "COMPANY_OFFICER_WITH_MULTIPLE_ROLES"
    COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP = (
        "COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP"
    )


# Local field names (for errors)
class Field(StringType):
    COUNTRY_OF_INCORPORATION = "COUNTRY_OF_INCORPORATION"


class CommercialRelationshipType(StringType, metaclass=EnumMeta):
    PASSFORT = "PASSFORT"
    DIRECT = "DIRECT"


class ErrorType(StringType, metaclass=EnumMeta):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_CONFIG = "INVALID_CONFIG"
    MISSING_CHECK_INPUT = "MISSING_CHECK_INPUT"
    INVALID_CHECK_INPUT = "INVALID_CHECK_INPUT"
    PROVIDER_CONNECTION = "PROVIDER_CONNECTION"
    PROVIDER_MESSAGE = "PROVIDER_MESSAGE"
    UNSUPPORTED_DEMO_RESULT = "UNSUPPORTED_DEMO_RESULT"


class ErrorSubType(StringType, metaclass=EnumMeta):
    # INVALID_CHECK_INPUT
    UNSUPPORTED_COUNTRY = "UNSUPPORTED_COUNTRY"


class EntityType(StringType, metaclass=EnumMeta):
    COMPANY = "COMPANY"
    INDIVIDUAL = "INDIVIDUAL"


class AddressType(StringType, metaclass=EnumMeta):
    STRUCTURED = "STRUCTURED"


class ProviderConfig(BaseModel):
    ...


class ProviderCredentials(BaseModel):
    apikey = StringType(required=True)


class Error(BaseModel):
    type = ErrorType(required=True)
    sub_type = ErrorSubType()
    message = StringType(required=True)
    data = DictType(StringType(), default=None)

    @staticmethod
    def unsupported_country():
        return Error(
            {
                "type": ErrorType.INVALID_CHECK_INPUT,
                "sub_type": ErrorSubType.UNSUPPORTED_COUNTRY,
                "message": "Country not supported.",
            }
        )

    @staticmethod
    def missing_required_field(field: str):
        return Error(
            {
                "type": ErrorType.MISSING_CHECK_INPUT,
                "data": {
                    "field": field,
                },
                "message": f"Missing required field ({field})",
            }
        )


class Warn(BaseModel):
    type = ErrorType(required=True)
    message = StringType(required=True)


class StructuredAddress(BaseModel):
    country = StringType(required=True)
    state_province = StringType(default=None)
    county = StringType(default=None)
    postal_code = StringType(default=None)
    locality = StringType(default=None)
    postal_town = StringType(default=None)
    route = StringType(default=None)
    street_number = StringType(default=None)
    premise = StringType(default=None)
    subpremise = StringType(default=None)
    address_lines = ListType(StringType(), default=None)


class Address(StructuredAddress):
    type = AddressType(required=True, default=AddressType.STRUCTURED)
    original_freeform_address = StringType(default=None)
    text = StringType(default=None)
    original_structured_address: Optional[StructuredAddress] = ModelType(
        StructuredAddress, default=None
    )


class CompanyAddressType(StringType, metaclass=EnumMeta):
    REGISTERED_ADDRESS = "registered_address"
    BRANCH_ADDRESS = "branch_address"
    HEAD_OFFICE_ADDRESS = "head_office_address"
    CONTACT_ADDRESS = "contact_address"
    TRADING_ADDRESS = "trading_address"


class CompanyAddress(BaseModel):
    type = CompanyAddressType(required=True)
    address = ModelType(Address, required=True)


class ContactDetails(BaseModel):
    email = StringType(default=None)
    phone_number = StringType(default=None)
    url = StringType(default=None)


class IndustryClassificationType(StringType, metaclass=EnumMeta):
    SIC = "SIC"
    NACE = "NACE"
    NAICS = "NAICS"
    OTHER = "OTHER"


class IndustryClassification(BaseModel):
    classification_type = IndustryClassificationType(required=True)
    code = StringType(required=True)
    classification_version = StringType(default=None)
    description = StringType(default=None)


class CompanyMetadata(BaseModel):
    name = StringType(default=None)
    number = StringType(default=None)
    lei = StringType(default=None)
    isin = StringType(default=None)
    lei = StringType(default=None)

    company_type = StringType(default=None)
    # structured_company_type = ModelType(StructuredCompanyType)
    industry_classifications = ListType(ModelType(IndustryClassification), default=None)

    # tax_ids = ListType(ModelType(TaxId), default=list, required=True)

    country_of_incorporation = StringType(default=None)
    incorporation_date = DateType(default=None)

    contact_information = ModelType(ContactDetails, default=None)
    addresses = ListType(ModelType(CompanyAddress), default=None)

    is_active = BooleanType(default=None)
    is_active_details = StringType(default=None)
    trade_description = StringType(default=None)
    description = StringType(default=None)


class ProviderRef(BaseModel):
    reference = StringType(required=True)
    label = StringType(required=True)


class ExternalRefs(BaseModel):
    provider = ListType(ModelType(ProviderRef), required=True)


class AssociatedRole(StringType, metaclass=EnumMeta):
    SHAREHOLDER = "SHAREHOLDER"
    BENEFICIAL_OWNER = "BENEFICIAL_OWNER"
    GLOBAL_ULTIMATE_OWNER = "GLOBAL_ULTIMATE_OWNER"
    CONTROLLING_SHAREHOLDER = "CONTROLLING_SHAREHOLDER"
    DIRECTOR = "DIRECTOR"
    COMPANY_SECRETARY = "COMPANY_SECRETARY"
    PARTNER = "PARTNER"


class TaxIdType(StringType, metaclass=EnumMeta):
    Ein = "EIN"
    Eurovat = "EUROVAT"
    Other = "OTHER"
    Vat = "VAT"


class TaxId(BaseModel):
    tax_id_name = StringType(default=None)
    tax_id_type = TaxIdType(required=True)
    value = StringType(required=True)


class CompanyStructureOwnershipType(StringType, metaclass=EnumMeta):
    Association = "ASSOCIATION"
    Company = "COMPANY"
    Other = "OTHER"
    Partnership = "PARTNERSHIP"
    SoleProprietorship = "SOLE_PROPRIETORSHIP"
    Trust = "TRUST"


class CompanyStructureType(BaseModel):
    is_limited = BooleanType(default=None)
    is_public = BooleanType(default=None)
    ownership_type = CompanyStructureOwnershipType(default=None)


class TenureType(StringType, metaclass=EnumMeta):
    CURRENT = "CURRENT"
    FORMER = "FORMER"


class Tenure(BaseModel):
    tenure_type = TenureType(required=True)


class CurrentTenure(Tenure):
    start = DateType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("tenure_type") == TenureType.CURRENT


class FormerTenure(Tenure):
    start = DateType(default=None)
    end = DateType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("tenure_type") == TenureType.FORMER


class Relationship(BaseModel):
    associated_role = AssociatedRole(required=True)
    tenure = PolyModelType(Tenure, required=True)


class DirectorRelationship(Relationship):
    original_role = StringType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.DIRECTOR


class PartnerRelationship(Relationship):
    original_role = StringType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.PARTNER


class Shareholding(BaseModel):
    share_class = StringType(default=None)
    amount = IntType(default=None)
    percentage = FloatType(default=None)


class ShareholderRelationship(Relationship):
    total_percentage = FloatType(default=None)
    shareholdings = ListType(ModelType(Shareholding), default=list)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.SHAREHOLDER


class BeneficialOwner(Relationship):
    total_percentage = FloatType(default=None)
    shareholdings = ListType(ModelType(Shareholding), default=list)

    distance = IntType(default=None)
    calculated_percentage = FloatType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.BENEFICIAL_OWNER


class GlobalUltimateOwner(Relationship):
    distance = IntType(default=None)
    calculated_percentage = FloatType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.GLOBAL_ULTIMATE_OWNER


class ControllingShareholder(Relationship):
    distance = IntType(default=None)
    calculated_percentage = FloatType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("associated_role") == AssociatedRole.CONTROLLING_SHAREHOLDER


class EntityData(BaseModel):
    entity_type = EntityType(required=True)


class AssociatedEntity(BaseModel):
    associate_id = UUIDType(required=True)
    entity_type = EntityType(required=True)
    immediate_data = PolyModelType(EntityData, required=True)
    relationships = ListType(PolyModelType(Relationship), default=list)


class Name(BaseModel):
    given_names = ListType(StringType, default=list)
    family_name = StringType(default=None)


class PersonalDetails(BaseModel):
    name = ModelType(Name, default=None)


class IndividualData(EntityData):
    entity_type = EntityType(required=True)
    personal_details = ModelType(PersonalDetails, default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("entity_type") == EntityType.INDIVIDUAL


class CheckedCompanyDataField(StringType, metaclass=EnumMeta):
    NAME = "NAME"
    NUMBER = "NUMBER"
    IS_ACTIVE = "IS_ACTIVE"
    LEI = "LEI"
    COUNTRY_OF_INCORPORATION = "COUNTRY_OF_INCORPORATION"
    ADDRESS = "ADDRESS"


class CompanyFieldCheckResult(StringType, metaclass=EnumMeta):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"


class CompanyFieldCheck(BaseModel):
    field = CheckedCompanyDataField()
    result = CompanyFieldCheckResult()


class CompanyData(EntityData):
    external_refs = ModelType(ExternalRefs, default=None)
    entity_type = EntityType(default=None)
    metadata = ModelType(CompanyMetadata, default=None)
    associated_entities = ListType(ModelType(AssociatedEntity), default=list)
    field_checks = ListType(ModelType(CompanyFieldCheck), default=list)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("entity_type") == EntityType.COMPANY

    def get_country_of_incorporation(self):
        if self.metadata:
            return self.metadata.country_of_incorporation

    def get_company_name(self):
        if self.metadata:
            return self.metadata.name

    def get_company_number(self):
        if self.metadata:
            return self.metadata.number


class Charge(BaseModel):
    amount = IntType(required=True)
    reference = StringType(default=None)
    sku = StringType(default=None)


class SearchInput(BaseModel):
    query = StringType(required=True)
    country_of_incorporation = StringType(required=True)
    state_of_incorporation = StringType(default=None)


class SearchRequest(BaseModel):
    demo_result = DemoResultType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    search_input: SearchInput = ModelType(SearchInput, required=True)
    provider_config: ProviderConfig = ModelType(ProviderConfig, required=True)
    provider_credentials: Optional[ProviderCredentials] = ModelType(
        ProviderCredentials, default=None
    )


class SearchCandidate(BaseModel):
    name = StringType(default=None)
    number_label = StringType(default=None)
    number = StringType(default=None)
    country_of_incorporation = StringType(default=None)
    status = StringType(default=None)
    provider_reference = ModelType(ProviderRef, default=None)
    addresses = ListType(ModelType(CompanyAddress), default=None)
    contact = ModelType(ContactDetails, default=None)
    incorporation_date = DateType(default=None)
    tax_ids = ListType(ModelType(TaxId), default=None)
    structure_type = ModelType(CompanyStructureType)
    lei = StringType(default=None)


class SearchResponse(BaseModel):
    search_output: List[SearchCandidate] = ListType(
        ModelType(SearchCandidate), default=[]
    )
    errors: List[Error] = ListType(ModelType(Error), default=[])
    warnings: List[Warn] = ListType(ModelType(Warn), default=[])
    provider_data = BaseType(default=None)
    charges = ListType(ModelType(Charge), default=[])

    @staticmethod
    def error(errors: List[Error]) -> "SearchResponse":
        res = SearchResponse()
        res.errors = errors
        return res


SUPPORTED_COUNTRIES = ["GBR", "USA", "CAN", "NLD"]
