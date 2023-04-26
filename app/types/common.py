from enum import Enum, EnumMeta
from typing import Any, Dict, List, Optional, Union

from pydantic import BaseModel, Field, constr
from typing_extensions import Literal


class MetaEnum(EnumMeta):
    def __contains__(cls, item):
        try:
            cls(item)
        except ValueError:
            return False
        return True


class BaseEnum(str, Enum, metaclass=MetaEnum):
    ...


class Date(BaseModel):
    __root__: constr(regex=r"(^\d{4}-\d{2}-\d{2}$)") = Field(
        ...,
        description="Exact date in `YYYY-MM-DD` format",
        example="1992-11-24",
        title="Date",
    )


class UUID(BaseModel):
    __root__: constr(
        regex=r"^[a-fA-F0-9]{8}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{4}-[a-fA-F0-9]{12}$"
    ) = Field(
        ...,
        description="[Universally unique identifier.](https://en.wikipedia.org/wiki/Universally_unique_identifier)",
        example="01234567-89ab-cdef-0123-456789abcdef",
        title="UUID",
    )


# Intentionally non-exhaustive
class DemoResultType(BaseEnum):
    ANY = "ANY"
    ANY_CHARGE = "ANY_CHARGE"
    NO_MATCH = "NO_MATCH"

    # Errors
    ERROR_INVALID_CREDENTIALS = "ERROR_INVALID_CREDENTIALS"
    ERROR_ANY_PROVIDER_MESSAGE = "ERROR_ANY_PROVIDER_MESSAGE"
    ERROR_CONNECTION_TO_PROVIDER = "ERROR_CONNECTION_TO_PROVIDER"

    # External resources
    EXTERNAL_RESOURCE_LINK = "EXTERNAL_RESOURCE_LINK"
    EXTERNAL_RESOURCE_EMBED = "EXTERNAL_RESOURCE_EMBED"

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
    COMPANY_RESIGNED_OFFICER = "COMPANY_RESIGNED_OFFICER"
    COMPANY_FORMER_SHAREHOLDER = "COMPANY_FORMER_SHAREHOLDER"
    COMPANY_OFFICER_WITH_MULTIPLE_ROLES = "COMPANY_OFFICER_WITH_MULTIPLE_ROLES"
    COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP = (
        "COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP"
    )


# Local field names (for errors)
class LocalField(BaseEnum):
    COUNTRY_OF_INCORPORATION = "COUNTRY_OF_INCORPORATION"


class CommercialRelationshipType(BaseEnum):
    PASSFORT = "PASSFORT"
    DIRECT = "DIRECT"


class ErrorType(BaseEnum):
    INVALID_CREDENTIALS = "INVALID_CREDENTIALS"
    INVALID_CONFIG = "INVALID_CONFIG"
    MISSING_CHECK_INPUT = "MISSING_CHECK_INPUT"
    INVALID_CHECK_INPUT = "INVALID_CHECK_INPUT"
    INVALID_INPUT = "INVALID_INPUT"
    PROVIDER_CONNECTION = "PROVIDER_CONNECTION"
    PROVIDER_MESSAGE = "PROVIDER_MESSAGE"
    UNSUPPORTED_DEMO_RESULT = "UNSUPPORTED_DEMO_RESULT"


class ErrorSubType(BaseEnum):
    # INVALID_CHECK_INPUT
    UNSUPPORTED_COUNTRY = "UNSUPPORTED_COUNTRY"


class EntityType(BaseEnum):
    COMPANY = "COMPANY"
    INDIVIDUAL = "INDIVIDUAL"


class AddressType(BaseEnum):
    STRUCTURED = "STRUCTURED"
    FREEFORM = "FREEFORM"


class ProviderConfig(BaseModel):
    ...


class ProviderCredentials(BaseModel):
    apikey: str


class Error(BaseModel):
    type: ErrorType
    sub_type: Optional[ErrorSubType]
    message: Optional[str]
    data: Optional[Dict] = None

    @staticmethod
    def unsupported_country():
        return Error(
            **{
                "type": ErrorType.INVALID_CHECK_INPUT,
                "sub_type": ErrorSubType.UNSUPPORTED_COUNTRY,
                "message": "Country not supported.",
            }
        )

    @staticmethod
    def missing_required_field(field: str):
        return Error(
            **{
                "type": ErrorType.MISSING_CHECK_INPUT,
                "data": {
                    "field": field,
                },
                "message": f"Missing required field ({field})",
            }
        )


class Warn(BaseModel):
    type: ErrorType
    message: str


class StructuredAddress(BaseModel):
    country: str
    state_province: Optional[str]
    county: Optional[str]
    postal_code: Optional[str]
    locality: Optional[str]
    postal_town: Optional[str]
    route: Optional[str]
    street_number: Optional[str]
    premise: Optional[str]
    subpremise: Optional[str]
    address_lines: Optional[List[str]]


class Address(StructuredAddress):
    type: AddressType = AddressType.STRUCTURED
    original_freeform_address: Optional[str]
    text: Optional[str]
    original_structured_address: Optional[StructuredAddress]


class CompanyAddressType(BaseEnum):
    REGISTERED_ADDRESS = "registered_address"
    BRANCH_ADDRESS = "branch_address"
    HEAD_OFFICE_ADDRESS = "head_office_address"
    CONTACT_ADDRESS = "contact_address"
    TRADING_ADDRESS = "trading_address"


class CompanyAddress(BaseModel):
    type: CompanyAddressType
    address: Address


class ContactDetails(BaseModel):
    email: Optional[str]
    phone_number: Optional[str]
    url: Optional[str]


class IndustryClassificationType(BaseEnum):
    SIC = "SIC"
    NACE = "NACE"
    NAICS = "NAICS"
    OTHER = "OTHER"


class IndustryClassification(BaseModel):
    classification_type: IndustryClassificationType
    code: str
    classification_version: Optional[str]
    description: Optional[str]


class CompanyMetadata(BaseModel):
    name: Optional[str]
    number: Optional[str]
    lei: Optional[str]
    isin: Optional[str]
    lei: Optional[str]

    company_type: Optional[str]
    # structured_company_type = ModelType(StructuredCompanyType)
    industry_classifications: Optional[List[IndustryClassification]]

    # tax_ids = ListType(ModelType(TaxId), default=list, required=True)

    country_of_incorporation: Optional[str]
    incorporation_date: Optional[Date]

    contact_information: Optional[ContactDetails]
    addresses: Optional[List[CompanyAddress]]

    is_active: Optional[bool]
    is_active_details: Optional[str]
    trade_description: Optional[str]
    description: Optional[str]


class ProviderRef(BaseModel):
    reference: str
    label: str


class ExternalRefs(BaseModel):
    provider: List[ProviderRef]
    generic: Optional[str]


class AssociatedRole(BaseEnum):
    SHAREHOLDER = "SHAREHOLDER"
    BENEFICIAL_OWNER = "BENEFICIAL_OWNER"
    GLOBAL_ULTIMATE_OWNER = "GLOBAL_ULTIMATE_OWNER"
    CONTROLLING_SHAREHOLDER = "CONTROLLING_SHAREHOLDER"
    DIRECTOR = "DIRECTOR"
    COMPANY_SECRETARY = "COMPANY_SECRETARY"
    PARTNER = "PARTNER"
    PERSON_OF_SIGNIFICANT_CONTROL = "PERSON_OF_SIGNIFICANT_CONTROL"


class TaxIdType(BaseEnum):
    Ein = "EIN"
    Eurovat = "EUROVAT"
    Other = "OTHER"
    Vat = "VAT"


class TaxId(BaseModel):
    tax_id_name: Optional[str]
    tax_id_type: TaxIdType
    value: str


class CompanyStructureOwnershipType(BaseEnum):
    Association = "ASSOCIATION"
    Company = "COMPANY"
    Other = "OTHER"
    Partnership = "PARTNERSHIP"
    SoleProprietorship = "SOLE_PROPRIETORSHIP"
    Trust = "TRUST"


class CompanyStructureType(BaseModel):
    is_limited: Optional[bool]
    is_public: Optional[bool]
    ownership_type: Optional[CompanyStructureOwnershipType]


class TenureType(BaseEnum):
    CURRENT = "CURRENT"
    FORMER = "FORMER"


class Tenure(BaseModel):
    tenure_type: TenureType


class CurrentTenure(Tenure):
    tenure_type = TenureType.CURRENT
    start: Optional[Date]


class FormerTenure(Tenure):
    tenure_type = TenureType.FORMER
    start: Optional[Date]
    end: Optional[Date]


class Relationship(BaseModel):
    associated_role: AssociatedRole
    tenure: Optional[Union[FormerTenure, CurrentTenure]]


class DirectorRelationship(Relationship):
    associated_role: Literal[AssociatedRole.DIRECTOR]
    original_role: Optional[str]


class PartnerRelationship(Relationship):
    associated_role: Literal[AssociatedRole.PARTNER]
    original_role: Optional[str]


class Shareholding(BaseModel):
    share_class: Optional[str]
    amount: Optional[int]
    percentage: Optional[float]


class ShareholderRelationship(Relationship):
    associated_role: Literal[AssociatedRole.SHAREHOLDER]
    total_percentage: Optional[float]
    shareholdings: List[Shareholding] = []


class BeneficialOwner(Relationship):
    associated_role: Literal[AssociatedRole.BENEFICIAL_OWNER]
    total_percentage: Optional[float]
    shareholdings: List[Shareholding] = []

    distance: Optional[int]
    calculated_percentage: Optional[float]


class GlobalUltimateOwner(Relationship):
    associated_role: Literal[AssociatedRole.GLOBAL_ULTIMATE_OWNER]
    distance: Optional[int]
    calculated_percentage: Optional[float]


class ControllingShareholder(Relationship):
    associated_role: Literal[AssociatedRole.CONTROLLING_SHAREHOLDER]
    distance: Optional[int]
    calculated_percentage: Optional[float]


class PersonOfSignificantControl(Relationship):
    associated_role: Literal[AssociatedRole.PERSON_OF_SIGNIFICANT_CONTROL]
    distance: Optional[int]
    calculated_percentage: Optional[float]


class EntityData(BaseModel):
    entity_type: EntityType


class AssociatedEntity(BaseModel):
    associate_id: UUID
    entity_type: EntityType
    immediate_data: Union[
        "IndividualData",
        "CompanyData",
    ] = Field(..., discriminator="entity_type")
    relationships: List[
        Union[
            DirectorRelationship,
            PartnerRelationship,
            ShareholderRelationship,
            BeneficialOwner,
            GlobalUltimateOwner,
            ControllingShareholder,
            PersonOfSignificantControl,
            Relationship,
        ]
    ] = [Field(..., discriminator="associated_role")]


class Name(BaseModel):
    given_names: List[str] = []
    family_name: Optional[str]


class PersonalDetails(BaseModel):
    name: Optional[Name]


class IndividualData(EntityData):
    entity_type: Literal[EntityType.INDIVIDUAL]
    personal_details: Optional[PersonalDetails]


class CheckedCompanyDataField(BaseEnum):
    NAME = "NAME"
    NUMBER = "NUMBER"
    IS_ACTIVE = "IS_ACTIVE"
    LEI = "LEI"
    COUNTRY_OF_INCORPORATION = "COUNTRY_OF_INCORPORATION"
    ADDRESS = "ADDRESS"


class CompanyFieldCheckResult(BaseEnum):
    MATCH = "MATCH"
    MISMATCH = "MISMATCH"


class CompanyFieldCheck(BaseModel):
    field: CheckedCompanyDataField
    result: CompanyFieldCheckResult


class CompanyData(EntityData):
    entity_type: Literal[EntityType.COMPANY]
    external_refs: Optional[ExternalRefs]
    metadata: Optional[CompanyMetadata]
    # NB: no AssociatedEntity type here to avoid circular types
    associated_entities: List = []
    field_checks: List[CompanyFieldCheck] = []

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
    amount: int
    reference: Optional[str]
    sku: Optional[str]

class ExternalResourceType(BaseEnum):
    LINK = "LINK"
    EMBED = "EMBED"

class ExternalResource(BaseModel):
      type: ExternalResourceType
      url: str
      id: UUID
      label: str

class OperationRequest(BaseModel):
    demo_result: Optional[str]
    commercial_relationship: CommercialRelationshipType
    provider_config: ProviderConfig
    provider_credentials: Optional[ProviderCredentials]


class OperationResponse(BaseModel):
    errors: List[Error] = []
    warnings: List[Warn] = []
    provider_data: Optional[Any]

    @classmethod
    def error(cls, errors: List[Error], **kwargs) -> "OperationResponse":
        res = cls(**kwargs)
        res.errors = errors
        return res


class SearchInput(BaseModel):
    query: str
    country_of_incorporation: str
    state_of_incorporation: Optional[str]


class SearchRequest(OperationRequest):
    search_input: SearchInput


class SearchCandidate(BaseModel):
    name: Optional[str]
    number_label: Optional[str]
    number: Optional[str]
    country_of_incorporation: Optional[str]
    status: Optional[str]
    provider_reference: Optional[ProviderRef]
    addresses: Optional[List[CompanyAddress]]
    contact: Optional[ContactDetails]
    incorporation_date: Optional[Date]
    tax_ids: Optional[List[TaxId]]
    structure_type: Optional[CompanyStructureType]
    lei: Optional[str]


class SearchResponse(OperationResponse):
    search_output: List[SearchCandidate] = []
    charges: List[Charge] = []


SUPPORTED_COUNTRIES = ["GBR", "USA", "CAN", "NLD"]
