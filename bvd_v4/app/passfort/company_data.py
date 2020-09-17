from collections import defaultdict
from enum import Enum
from functools import reduce

from schematics.types import (
    DecimalType,
    StringType,
    DateTimeType,
    DictType,
    ListType,
    IntType,
    BaseType,
    ModelType,
    BooleanType,
    UUIDType,
    PolyModelType,
)

from app.constants import PROVIDER_NAME
from app.passfort.base_model import BaseModel
from app.passfort.types import (
    country_alpha_2_to_3,
    format_names,
    CompanyMetadata,
    EntityType,
    Error,
    Shareholding,
)


def build_resolver_id(original_id):
    from uuid import NAMESPACE_X500, uuid3
    return uuid3(NAMESPACE_X500, original_id)


class AssociateCompanyMetadata(BaseModel):
    bvd_id = StringType(required=True)
    name = StringType(required=True)
    lei = StringType()
    country_of_incorporation = StringType(min_length=3, max_length=3)
    state_of_incorporation = StringType()

    def from_bvd_shareholder(index, bvd_data):
        # TODO: Shareholder SIC codes
        return AssociateCompanyMetadata({
            'bvd_id': bvd_data.shareholder_bvd_id[index],
            'name': bvd_data.shareholder_name[index],
            'country_of_incorporation': country_alpha_2_to_3(bvd_data.shareholder_country_code[index]),
            'state_of_incorporation': bvd_data.shareholder_state_province[index],
            'lei': bvd_data.shareholder_lei[index],

        })

    def merge(a, b):
        return AssociateCompanyMetadata({
            'bvd_id': a.bvd_id or b.bvd_id,
            'name': a.name or b.name,
            'country_of_incorporation': a.country_of_incorporation or b.country_of_incorporation,
            'state_of_incorporation': a.state_of_incorporation or b.state_of_incorporation,
            'lei': a.lei or b.lei,
        })


class FullName(BaseModel):
    title = StringType()
    first_names = ListType(StringType(), default=list, required=True)
    last_name = StringType()

    def from_bvd_shareholder(index, bvd_data):
        title, first_names, last_name = format_names(
            bvd_data.shareholder_first_name[index],
            bvd_data.shareholder_last_name[index],
            bvd_data.shareholder_name[index],
            EntityType.INDIVIDUAL,
        )
        return FullName({
            "title": title,
            "first_names": first_names,
            "last_name": last_name,
        })

    def from_bvd_beneficial_owner(index, bvd_data):
        title, first_names, last_name = format_names(
            bvd_data.beneficial_owner_first_name[index],
            bvd_data.beneficial_owner_last_name[index],
            bvd_data.beneficial_owner_name[index],
            EntityType.INDIVIDUAL,
        )
        return FullName({
            "title": title,
            "first_names": first_names,
            "last_name": last_name,
        })

    def merge(a, b):
        return FullName({
            "title": a.title or b.title,
            "first_names": a.first_names or b.first_names,
            "last_name": a.last_name or b.last_name,
        })


class AssociatePersonalDetails(BaseModel):
    name = ModelType(FullName, required=True)
    dob = DateTimeType(default=None)
    nationality = StringType(min_length=3, max_length=3, default=None)

    def from_bvd_shareholder(index, bvd_data):
        return AssociatePersonalDetails({
            'name': FullName.from_bvd_shareholder(index, bvd_data),
            'nationality': country_alpha_2_to_3(bvd_data.shareholder_country_code[index])
        })

    def from_bvd_beneficial_owner(index, bvd_data):
        return AssociatePersonalDetails({
            'name': FullName.from_bvd_beneficial_owner(index, bvd_data),
            'nationality': country_alpha_2_to_3(bvd_data.beneficial_owner_country_code[index])
        })

    def merge(a, b):
        return AssociatePersonalDetails({
            'name': FullName.merge(a.name, b.name),
            'nationality': a.nationality or b.nationality,
        })


class AssociateEntityData(BaseModel):
    entity_type = StringType(choices=[ty.value for ty in EntityType], required=True)

    def from_bvd_shareholder(entity_type, index, bvd_data):
        if entity_type == EntityType.COMPANY:
            return CompanyAssociateData.from_bvd_shareholder(index, bvd_data)
        else:
            return IndividualAssociateData.from_bvd_shareholder(index, bvd_data)

    def from_bvd_beneficial_owner(index, bvd_data):
        return IndividualAssociateData.from_bvd_beneficial_owner(index, bvd_data)

    def merge(a, b):
        if a.entity_type == EntityType.COMPANY:
            return CompanyAssociateData.merge(a, b)
        else:
            return IndividualAssociateData.merge(a, b)


class CompanyAssociateData(AssociateEntityData):
    metadata = ModelType(AssociateCompanyMetadata, required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get('enitity_type') == EntityType.COMPANY.value

    def from_bvd_shareholder(index, bvd_data):
        return CompanyAssociateData({
            'entity_type': EntityType.COMPANY.value,
            'metadata': AssociateCompanyMetadata.from_bvd_shareholder(index, bvd_data)
        })

    def merge(a, b):
        return CompanyAssociateData({
            'entity_type': EntityType.COMPANY.value,
            'metadata': AssociateCompanyMetadata.merge(a.metadata, b.metadata)
        })


class IndividualAssociateData(AssociateEntityData):
    personal_details = ModelType(AssociatePersonalDetails, required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get('enitity_type') == EntityType.INDIVIDUAL.value

    def from_bvd_shareholder(index, bvd_data):
        return IndividualAssociateData({
            'entity_type': EntityType.INDIVIDUAL.value,
            'personal_details': AssociatePersonalDetails.from_bvd_shareholder(index, bvd_data)
        })

    def from_bvd_beneficial_owner(index, bvd_data):
        return IndividualAssociateData({
            'entity_type': EntityType.INDIVIDUAL.value,
            'personal_details': AssociatePersonalDetails.from_bvd_beneficial_owner(index, bvd_data)
        })

    def merge(a, b):
        return IndividualAssociateData({
            'entity_type': EntityType.INDIVIDUAL.value,
            'personal_details': AssociatePersonalDetails.merge(a.personal_details, b.personal_details),
        })


class RelationshipType(Enum):
    SHAREHOLDER = "SHAREHOLDER"


class AssociatedRole(Enum):
    SHAREHOLDER = "SHAREHOLDER"
    BENEFICIAL_OWNER = "BENEFICIAL_OWNER"


class Relationship(BaseModel):
    relationship_type = StringType(required=True, choices=[ty.value for ty in RelationshipType])
    associated_role = StringType(required=True, choices=[role.value for role in AssociatedRole])

    def from_bvd_shareholder(index, bvd_data):
        return ShareholderRelationship.from_bvd_shareholder(index, bvd_data)

    def from_bvd_beneficial_owner(index, bvd_data):
        return Relationship({
            "relationship_type": RelationshipType.SHAREHOLDER.value,
            "associated_role": AssociatedRole.BENEFICIAL_OWNER.value,
        })


class ShareholderRelationship(Relationship):
    shareholdings = ListType(ModelType(Shareholding), required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get('relationship_type') == RelationshipType.SHAREHOLDER.value

    def from_bvd_shareholder(index, bvd_data):
        return ShareholderRelationship({
            "relationship_type": RelationshipType.SHAREHOLDER.value,
            "associated_role": AssociatedRole.SHAREHOLDER.value,
            "shareholdings": [
                Shareholding.from_bvd(bvd_data.shareholder_direct_percentage[index])
            ]
        })


class Associate(BaseModel):
    associate_id = UUIDType(required=True)
    entity_type = StringType(choices=[ty.value for ty in EntityType], required=True)
    immediate_data = ModelType(AssociateEntityData, required=True)
    relationships = ListType(ModelType(Relationship), required=True)

    def from_bvd_shareholder(index, bvd_data):
        entity_type = EntityType.INDIVIDUAL if bvd_data.shareholder_is_individual(index) else EntityType.COMPANY
        return Associate({
            'associate_id': build_resolver_id(bvd_data.shareholder_bvd_id[index]),
            'entity_type': entity_type.value,
            'immediate_data': AssociateEntityData.from_bvd_shareholder(entity_type, index, bvd_data),
            'relationships': [Relationship.from_bvd_shareholder(index, bvd_data)],
        })

    def from_bvd_beneficial_owner(index, bvd_data):
        return Associate({
            'associate_id': build_resolver_id(bvd_data.beneficial_owner_bvd_id[index]),
            # UBOs are always individuals
            'entity_type': EntityType.INDIVIDUAL.value,
            'immediate_data': AssociateEntityData.from_bvd_beneficial_owner(index, bvd_data),
            'relationships': [
                Relationship.from_bvd_beneficial_owner(index, bvd_data),
            ],
        })

    def merge(a, b):
        return Associate({
            'associate_id': a.associate_id,
            'entity_type': a.entity_type,
            'immediate_data': AssociateEntityData.merge(a.immediate_data, b.immediate_data),
            'relationships': a.relationships + b.relationships,
        })


def merge_associates_by_id(associates):
    keyed_by_id = defaultdict(list)

    for associate in associates:
        keyed_by_id[associate.associate_id].append(associate)

    return [
        reduce(Associate.merge, matching_associates)
        for matching_associates
        in keyed_by_id.values()
    ]


class CompanyData(BaseModel):
    metadata = ModelType(CompanyMetadata, required=True)
    associated_entities = ListType(ModelType(Associate), required=True)

    def from_bvd(bvd_data):
        shareholders = [
            Associate.from_bvd_shareholder(index, bvd_data)
            for index
            in range(0, len(bvd_data.shareholder_bvd_id))
        ]
        beneficial_owners = [
            Associate.from_bvd_beneficial_owner(index, bvd_data)
            for index
            in range(0, len(bvd_data.beneficial_owner_bvd_id))
        ]

        return CompanyData({
            'metadata': CompanyMetadata.from_bvd(bvd_data),
            'associated_entities': merge_associates_by_id(shareholders + beneficial_owners),
        })


class CompanyDataCheckResponse(BaseModel):
    output_data = ModelType(CompanyData, serialize_when_none=True)
    errors = ListType(ModelType(Error), serialize_when_none=True, default=list)
    price = IntType()
    raw = BaseType()
