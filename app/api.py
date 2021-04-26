import inspect
from functools import wraps
from typing import Iterable, TypeVar, Optional, Type, List

from schematics import Model
from schematics.common import NOT_NONE
from schematics.types import (
    FloatType, UUIDType, StringType, ModelType, ListType, DateType, BaseType, DictType, IntType,
    BooleanType, PolyModelType
)
from schematics.exceptions import DataError
from schematics.types.base import TypeMeta
from flask import abort, request, Response, jsonify


# Inheriting this class will make an enum exhaustive
class EnumMeta(TypeMeta):
    def __new__(mcs, name, bases, attrs):
        attrs['choices'] = [v for k, v in attrs.items(
        ) if not k.startswith('_') and k.isupper()]
        return TypeMeta.__new__(mcs, name, bases, attrs)


class ApproxDateType(DateType):
    formats = ['%Y-%m']


# Intentionally non-exhaustive
class DemoResultType(StringType):
    ANY = 'ANY'
    ANY_CHARGE = 'ANY_CHARGE'
    NO_MATCH = 'NO_MATCH'

    # Errors
    ERROR_INVALID_CREDENTIALS = 'ERROR_INVALID_CREDENTIALS'
    ERROR_ANY_PROVIDER_MESSAGE = 'ERROR_ANY_PROVIDER_MESSAGE'
    ERROR_CONNECTION_TO_PROVIDER = 'ERROR_CONNECTION_TO_PROVIDER'

    # Company search specific
    NO_HITS = 'NO_HITS'
    MANY_HITS = 'MANY_HITS'

    # Company data check specific
    NO_DATA = 'NO_DATA'
    ALL_DATA = 'ALL_DATA'
    COMPANY_INACTIVE = 'COMPANY_INACTIVE'
    COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH = 'COMPANY_COUNTRY_OF_INCORPORATION_MISMATCH'
    COMPANY_NAME_MISMATCH = 'COMPANY_NAME_MISMATCH'
    COMPANY_NUMBER_MISMATCH = 'COMPANY_NUMBER_MISMATCH'
    # Associates data
    COMPANY_RESGINED_OFFICER = 'COMPANY_RESIGNED_OFFICER'
    COMPANY_FORMER_SHAREHOLDER = 'COMPANY_FORMER_SHAREHOLDER'
    COMPANY_OFFICER_WITH_MULTIPLE_ROLES = 'COMPANY_OFFICER_WITH_MULTIPLE_ROLES'
    COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP = 'COMPANY_SHAREHOLDER_WITH_100_PERCENT_OWNERSHIP'


# Local field names (for errors)
class Field(StringType):
    COUNTRY_OF_INCORPORATION = 'COUNTRY_OF_INCORPORATION'


class CommercialRelationshipType(StringType, metaclass=EnumMeta):
    PASSFORT = 'PASSFORT'
    DIRECT = 'DIRECT'


class ErrorType(StringType, metaclass=EnumMeta):
    INVALID_CREDENTIALS = 'INVALID_CREDENTIALS'
    INVALID_CONFIG = 'INVALID_CONFIG'
    MISSING_CHECK_INPUT = 'MISSING_CHECK_INPUT'
    INVALID_CHECK_INPUT = 'INVALID_CHECK_INPUT'
    PROVIDER_CONNECTION = 'PROVIDER_CONNECTION'
    PROVIDER_MESSAGE = 'PROVIDER_MESSAGE'
    UNSUPPORTED_DEMO_RESULT = 'UNSUPPORTED_DEMO_RESULT'


class ErrorSubType(StringType, metaclass=EnumMeta):
    # INVALID_CHECK_INPUT
    UNSUPPORTED_COUNTRY = 'UNSUPPORTED_COUNTRY'


class EntityType(StringType, metaclass=EnumMeta):
    COMPANY = 'COMPANY'
    INDIVIDUAL = 'INDIVIDUAL'


class AddressType(StringType, metaclass=EnumMeta):
    STRUCTURED = 'STRUCTURED'


class ProviderConfig(Model):
    ...


class ProviderCredentials(Model):
    apikey = StringType(required=True)


class Error(Model):
    type = ErrorType(required=True)
    sub_type = ErrorSubType()
    message = StringType(required=True)
    data = DictType(StringType(), default=None)

    @staticmethod
    def unsupported_country():
        return Error({
            'type': ErrorType.INVALID_CHECK_INPUT,
            'sub_type': ErrorSubType.UNSUPPORTED_COUNTRY,
            'message': 'Country not supported.',
        })

    @staticmethod
    def missing_required_field(field: str):
        return Error({
            'type': ErrorType.MISSING_CHECK_INPUT,
            'data': {
                'field': field,
            },
            'message': f'Missing required field ({field})',
        })

    class Options:
        export_level = NOT_NONE


class Warn(Model):
    type = ErrorType(required=True)
    message = StringType(required=True)

    class Options:
        export_level = NOT_NONE


class StructuredAddress(Model):
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

    class Options:
        export_level = NOT_NONE


class Address(StructuredAddress):
    type = AddressType(required=True, default=AddressType.STRUCTURED)
    original_freeform_address = StringType(default=None)
    original_structured_address: Optional[StructuredAddress] = ModelType(
        StructuredAddress, default=None)


class CompanyAddressType(StringType, metaclass=EnumMeta):
    REGISTERED_ADDRESS = 'registered_address'
    BRANCH_ADDRESS = 'branch_address'
    HEAD_OFFICE_ADDRESS = 'head_office_address'
    CONTACT_ADDRESS = 'contact_address'
    TRADING_ADDRESS = 'trading_address'


class CompanyAddress(Model):
    type = CompanyAddressType(required=True)
    address = ModelType(Address, required=True)


class ContactDetails(Model):
    email = StringType(default=None)
    phone_number = StringType(default=None)
    url = StringType(default=None)

    class Options:
        export_level = NOT_NONE


class IndustryClassificationType(StringType, metaclass=EnumMeta):
    SIC = "SIC"
    NACE = "NACE"
    NAICS = "NAICS"
    OTHER = "OTHER"


class IndustryClassification(Model):
    classification_type = IndustryClassificationType(required=True)
    code = StringType(required=True)
    classification_version = StringType(default=None)
    description = StringType(default=None)

    class Options:
        export_level = NOT_NONE


class CompanyMetadata(Model):
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


class ProviderRef(Model):
    reference = StringType(required=True)
    label = StringType(required=True)


class ExternalRefs(Model):
    provider = ListType(ModelType(ProviderRef), required=True)


class RelationshipType(StringType, metaclass=EnumMeta):
    SHAREHOLDER = "SHAREHOLDER"
    OFFICER = "OFFICER"


class AssociatedRole(StringType, metaclass=EnumMeta):
    SHAREHOLDER = "SHAREHOLDER"

    DIRECTOR = "DIRECTOR"
    COMPANY_SECRETARY = "COMPANY_SECRETARY"
    PARTNER = "PARTNER"


class TenureType(StringType, metaclass=EnumMeta):
    CURRENT = 'CURRENT'
    FORMER = 'FORMER'


class Tenure(Model):
    tenure_type = TenureType(required=True)

    class Options:
        export_level = NOT_NONE


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


class Relationship(Model):
    associated_role = AssociatedRole(required=True)
    relationship_type = RelationshipType(required=True)
    tenure = PolyModelType(Tenure, required=True)

    class Options:
        export_level = NOT_NONE


class OfficerRelationship(Relationship):
    original_role = StringType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("relationship_type") == RelationshipType.OFFICER


class ShareholderRelationship(Relationship):
    total_percentage = FloatType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("relationship_type") == RelationshipType.SHAREHOLDER


class EntityData(Model):
    entity_type = EntityType(required=True)


class AssociatedEntity(Model):
    associate_id = UUIDType(required=True)
    entity_type = EntityType(required=True)
    immediate_data = PolyModelType(EntityData, required=True)
    relationships = ListType(PolyModelType(Relationship), default=list)


class Name(Model):
    given_names = ListType(StringType, default=list)
    family_name = StringType(default=None)


class PersonalDetails(Model):
    name = ModelType(Name, default=None)


class IndividualData(EntityData):
    entity_type = EntityType(required=True)
    personal_details = ModelType(PersonalDetails, default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("entity_type") == EntityType.INDIVIDUAL


class CompanyData(EntityData):
    external_refs = ModelType(ExternalRefs, default=None)
    entity_type = EntityType(default=None)
    metadata = ModelType(CompanyMetadata, default=None)
    associated_entities = ListType(ModelType(AssociatedEntity), default=list)

    class Options:
        export_level = NOT_NONE

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


class Charge(Model):
    amount = IntType(required=True)
    reference = StringType(default=None)
    sku = StringType(default=None)

    class Options:
        export_level = NOT_NONE


class RunCheckRequest(Model):
    id = UUIDType(required=True)
    demo_result = DemoResultType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    check_input: CompanyData = ModelType(CompanyData, required=True)
    provider_config: ProviderConfig = ModelType(ProviderConfig, required=True)
    provider_credentials: Optional[ProviderCredentials] = ModelType(
        ProviderCredentials, default=None)

    class Options:
        export_level = NOT_NONE


class RunCheckResponse(Model):
    check_output: Optional[CompanyData] = ModelType(CompanyData, default=None)
    errors: List[Error] = ListType(ModelType(Error), default=[])
    warnings: List[Warn] = ListType(ModelType(Warn), default=[])
    provider_data = BaseType(default=None)
    charges = ListType(ModelType(Charge), default=[])

    @staticmethod
    def error(errors: List[Error]) -> 'RunCheckResponse':
        res = RunCheckResponse()
        res.errors = errors
        return res

    def patch_to_match_input(self, check_input):
        if self.check_output:
            if self.check_output.metadata:
                self.check_output.metadata.country_of_incorporation = (
                    check_input.country_of_incorporation or self.check_output.metadata.country_of_incorporation
                )
                self.check_output.metadata.name = check_input.name or self.check_output.metadata.name
                self.check_output.metadata.number = check_input.number or self.check_output.metadata.number

    class Options:
        export_level = NOT_NONE


T = TypeVar('T')


def _first(x: Iterable[T]) -> Optional[T]:
    return next(iter(x), None)


def _get_input_annotation(signature: inspect.Signature) -> Optional[Type[Model]]:
    first_param: Optional[inspect.Parameter] = _first(
        signature.parameters.values())
    if first_param is None:
        return None

    if first_param.kind not in [inspect.Parameter.POSITIONAL_ONLY, inspect.Parameter.POSITIONAL_OR_KEYWORD]:
        return None

    if not issubclass(first_param.annotation, Model):
        return None

    return first_param.annotation


def validate_models(fn):
    """
3    Creates a Schematics Model from the request data and validates it.

    Throws DataError if invalid.
    Otherwise, it passes the validated request data to the wrapped function.
    """

    signature = inspect.signature(fn)

    assert issubclass(signature.return_annotation,
                      Model), 'Must have a return type annotation'
    output_model = signature.return_annotation
    input_model = _get_input_annotation(signature)

    @wraps(fn)
    def wrapped_fn(*args, **kwargs):
        if input_model is None:
            res = fn(*args, **kwargs)
        else:
            model = None
            try:
                model = input_model().import_data(request.json, apply_defaults=True)
                model.validate()
            except DataError as e:
                abort(Response(str(e), status=400))

            res = fn(model, *args, **kwargs)

        assert isinstance(res, output_model)

        return jsonify(res.serialize())

    return wrapped_fn


class SearchInput(Model):
    query = StringType(required=True)
    country_of_incorporation = StringType(required=True)
    state_of_incorporation = StringType(default=None)


class SearchRequest(Model):
    demo_result = DemoResultType(default=None)
    commercial_relationship = CommercialRelationshipType(required=True)
    search_input: SearchInput = ModelType(SearchInput, required=True)
    provider_config: ProviderConfig = ModelType(ProviderConfig, required=True)
    provider_credentials: Optional[ProviderCredentials] = ModelType(
        ProviderCredentials, default=None)

    class Options:
        export_level = NOT_NONE


class SearchCandidate(Model):
    name = StringType(default=None)
    number = StringType(default=None)
    country_of_incorporation = StringType(default=None)
    status = StringType(default=None)
    provider_reference = ModelType(ProviderRef, default=None)

    class Options:
        export_level = NOT_NONE


class SearchResponse(Model):
    search_output: List[SearchCandidate] = ListType(ModelType(SearchCandidate), default=[])
    errors: List[Error] = ListType(ModelType(Error), default=[])
    warnings: List[Warn] = ListType(ModelType(Warn), default=[])
    provider_data = BaseType(default=None)
    charges = ListType(ModelType(Charge), default=[])

    @staticmethod
    def error(errors: List[Error]) -> 'SearchResponse':
        res = SearchResponse()
        res.errors = errors
        return res

    class Options:
        export_level = NOT_NONE
