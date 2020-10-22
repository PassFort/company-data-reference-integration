import logging
from collections import defaultdict
from enum import Enum
from functools import reduce, partial

from schematics.common import DROP
from schematics.types.serializable import serializable
from schematics.types import (
    DecimalType,
    StringType,
    DateType,
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
from app.common import build_resolver_id
from app.passfort.base_model import BaseModel
from app.passfort.types import (
    country_alpha_2_to_3,
    country_names_to_alpha_3,
    format_names,
    CompanyMetadata,
    EntityType,
    Error,
    Shareholding,
)


class AssociateCompanyMetadata(BaseModel):
    bvd_id = StringType(required=True)
    name = StringType(required=True)
    lei = StringType()
    country_of_incorporation = StringType(min_length=3, max_length=3)
    state_of_incorporation = StringType()

    def from_bvd_shareholder(index, bvd_data):
        # TODO: Shareholder SIC codes
        return AssociateCompanyMetadata(
            {
                "bvd_id": bvd_data.shareholder_bvd_id[index],
                "name": bvd_data.shareholder_name[index],
                "country_of_incorporation": country_alpha_2_to_3(
                    bvd_data.shareholder_country_code[index]
                ),
                "state_of_incorporation": bvd_data.shareholder_state_province[index],
                "lei": bvd_data.shareholder_lei[index],
            }
        )

    def from_bvd_contact(index, bvd_data):
        # TODO: Officer metadata & SIC codes
        return AssociateCompanyMetadata(
            {
                "bvd_id": bvd_data.contact_bvd_id[index],
                "name": bvd_data.contact_name[index],
            }
        )

    @classmethod
    def merge(cls, a, b):
        return AssociateCompanyMetadata(
            {
                "bvd_id": a.bvd_id or b.bvd_id,
                "name": a.name or b.name,
                "country_of_incorporation": a.country_of_incorporation
                or b.country_of_incorporation,
                "state_of_incorporation": a.state_of_incorporation
                or b.state_of_incorporation,
                "lei": a.lei or b.lei,
            }
        )


class FullName(BaseModel):
    title = StringType()
    given_names = ListType(StringType(), default=list, required=True)
    family_name = StringType()

    def from_bvd_shareholder(index, bvd_data):
        title, first_names, last_name = format_names(
            bvd_data.shareholder_first_name[index],
            bvd_data.shareholder_last_name[index],
            bvd_data.shareholder_name[index],
            EntityType.INDIVIDUAL,
        )
        return FullName(
            {"title": title, "given_names": first_names, "family_name": last_name,}
        )

    def from_bvd_beneficial_owner(index, bvd_data):
        title, first_names, last_name = format_names(
            bvd_data.beneficial_owner_first_name[index],
            bvd_data.beneficial_owner_last_name[index],
            bvd_data.beneficial_owner_name[index],
            EntityType.INDIVIDUAL,
        )
        return FullName(
            {"title": title, "given_names": first_names, "family_name": last_name,}
        )

    def from_bvd_contact(index, bvd_data):
        title_from_full_name, first_names, last_name = format_names(
            bvd_data.contact_first_name[index],
            bvd_data.contact_last_name[index],
            bvd_data.contact_name[index],
            EntityType.INDIVIDUAL,
        )
        return FullName(
            {
                "title": title_from_full_name or bvd_data.contact_title[index],
                "given_names": first_names,
                "family_name": last_name,
            }
        )

    @classmethod
    def merge(cls, a, b):
        return FullName(
            {
                "title": a.title or b.title,
                "given_names": a.given_names or b.given_names,
                "family_name": a.family_name or b.family_name,
            }
        )


class AssociatePersonalDetails(BaseModel):
    name = ModelType(FullName, required=True)
    dob = DateType(default=None)
    nationality = StringType(min_length=3, max_length=3, default=None)

    def from_bvd_shareholder(index, bvd_data):
        return AssociatePersonalDetails(
            {
                "name": FullName.from_bvd_shareholder(index, bvd_data),
                "nationality": country_alpha_2_to_3(
                    bvd_data.shareholder_country_code[index]
                ),
            }
        )

    def from_bvd_beneficial_owner(index, bvd_data):
        return AssociatePersonalDetails(
            {
                "name": FullName.from_bvd_beneficial_owner(index, bvd_data),
                "nationality": country_alpha_2_to_3(
                    bvd_data.beneficial_owner_country_code[index]
                ),
            }
        )

    def from_bvd_contact(index, bvd_data):
        return AssociatePersonalDetails(
            {
                "name": FullName.from_bvd_contact(index, bvd_data),
                "dob": bvd_data.contact_date_of_birth[index],
                "nationality": country_names_to_alpha_3(
                    bvd_data.contact_nationality[index]
                ),
            }
        )

    @classmethod
    def merge(cls, a, b):
        return AssociatePersonalDetails(
            {
                "name": FullName.merge(a.name, b.name),
                "dob": a.dob or b.dob,
                "nationality": a.nationality or b.nationality,
            }
        )


class AssociateEntityData(BaseModel):
    entity_type = StringType(choices=[ty.value for ty in EntityType], required=True)

    def from_bvd_shareholder(entity_type, index, bvd_data):
        if entity_type == EntityType.COMPANY:
            return CompanyAssociateData.from_bvd_shareholder(index, bvd_data)
        else:
            return IndividualAssociateData.from_bvd_shareholder(index, bvd_data)

    def from_bvd_beneficial_owner(index, bvd_data):
        return IndividualAssociateData.from_bvd_beneficial_owner(index, bvd_data)

    def from_bvd_officer(entity_type, index, bvd_data):
        if entity_type == EntityType.COMPANY:
            return CompanyAssociateData.from_bvd_contact(index, bvd_data)
        else:
            return IndividualAssociateData.from_bvd_contact(index, bvd_data)

    @classmethod
    def merge(cls, a, b):
        if a.entity_type == EntityType.COMPANY.value:
            return CompanyAssociateData.merge(a, b)
        else:
            return IndividualAssociateData.merge(a, b)


class CompanyAssociateData(AssociateEntityData):
    metadata = ModelType(AssociateCompanyMetadata, required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("enitity_type") == EntityType.COMPANY.value

    def from_bvd_shareholder(index, bvd_data):
        return CompanyAssociateData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": AssociateCompanyMetadata.from_bvd_shareholder(
                    index, bvd_data
                ),
            }
        )

    def from_bvd_contact(index, bvd_data):
        return CompanyAssociateData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": AssociateCompanyMetadata.from_bvd_contact(index, bvd_data),
            }
        )

    @classmethod
    def merge(cls, a, b):
        return CompanyAssociateData(
            {
                "entity_type": EntityType.COMPANY.value,
                "metadata": AssociateCompanyMetadata.merge(a.metadata, b.metadata),
            }
        )


class IndividualAssociateData(AssociateEntityData):
    personal_details = ModelType(AssociatePersonalDetails, required=True)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("enitity_type") == EntityType.INDIVIDUAL.value

    def from_bvd_shareholder(index, bvd_data):
        return IndividualAssociateData(
            {
                "entity_type": EntityType.INDIVIDUAL.value,
                "personal_details": AssociatePersonalDetails.from_bvd_shareholder(
                    index, bvd_data
                ),
            }
        )

    def from_bvd_beneficial_owner(index, bvd_data):
        return IndividualAssociateData(
            {
                "entity_type": EntityType.INDIVIDUAL.value,
                "personal_details": AssociatePersonalDetails.from_bvd_beneficial_owner(
                    index, bvd_data
                ),
            }
        )

    def from_bvd_contact(index, bvd_data):
        return IndividualAssociateData(
            {
                "entity_type": EntityType.INDIVIDUAL.value,
                "personal_details": AssociatePersonalDetails.from_bvd_contact(
                    index, bvd_data
                ),
            }
        )

    @classmethod
    def merge(cls, a, b):
        return IndividualAssociateData(
            {
                "entity_type": EntityType.INDIVIDUAL.value,
                "personal_details": AssociatePersonalDetails.merge(
                    a.personal_details, b.personal_details
                ),
            }
        )


class RelationshipType(Enum):
    SHAREHOLDER = "SHAREHOLDER"
    OFFICER = "OFFICER"


class AssociatedRole(Enum):
    BENEFICIAL_OWNER = "BENEFICIAL_OWNER"

    DIRECTOR = "DIRECTOR"
    COMPANY_SECRETARY = "COMPANY_SECRETARY"
    RESIGNED_OFFICER = "RESIGNED_OFFICER"
    OTHER = "OTHER"

    def from_bvd_contacts_roles(index, bvd_data):
        original_role_lower = bvd_data.contact_role[index].lower()
        current_previous = bvd_data.contact_current_previous[index]

        if "shareholder" in original_role_lower:
            # Don't return previous shareholders - our api doesn't fully support them without a ceased on date.
            if current_previous != "Current":
                return None
            return AssociatedRole.BENEFICIAL_OWNER
        elif current_previous != "Current":
            return AssociatedRole.RESIGNED_OFFICER
        elif "director" in original_role_lower:
            return AssociatedRole.DIRECTOR
        elif "secretary" in original_role_lower:
            return AssociatedRole.COMPANY_SECRETARY
        else:
            return AssociatedRole.OTHER

    def is_potential_officer(self):
        return self != AssociatedRole.BENEFICIAL_OWNER

    def is_shareholder(self):
        return self == AssociatedRole.BENEFICIAL_OWNER


class Relationship(BaseModel):
    relationship_type = StringType(
        required=True, choices=[ty.value for ty in RelationshipType]
    )
    associated_role = StringType(
        required=True, choices=[role.value for role in AssociatedRole]
    )

    def from_bvd_shareholder(index, bvd_data):
        return ShareholderRelationship.from_bvd_shareholder(index, bvd_data)

    def from_bvd_beneficial_owner(index, bvd_data):
        return ShareholderRelationship.from_bvd_beneficial_owner(index, bvd_data)

    def from_bvd_contacts(index, bvd_data):
        passfort_role = AssociatedRole.from_bvd_contacts_roles(
            index, bvd_data
        )
        # Sometimes there is no relationship (e.g. previous shareholders)
        # We might decide to return them, but we'll need to change the data structure to do that
        # E.g actually send an 'is_active' field from the integration, since we won't always have
        # ceased_on dates.
        if passfort_role is None:
            return None
        if passfort_role.is_potential_officer():
            return OfficerRelationship(
                {
                    "original_role": bvd_data.contact_role[index],
                    "appointed_on": bvd_data.contact_appointment_date[index],
                    "resigned_on": bvd_data.contact_resignation_date[index],
                    "relationship_type": RelationshipType.OFFICER.value,
                    "associated_role": passfort_role.value,
                }
            )
        else:
            return ShareholderRelationship(
                {
                    "relationship_type": RelationshipType.SHAREHOLDER.value,
                    "associated_role": passfort_role.value,
                }
            )

    @classmethod
    def merge(cls, a, b):
        assert(a.relationship_type == b.relationship_type)
        assert(a.associated_role == b.associated_role)

        if AssociatedRole(a.associated_role).is_potential_officer():
            return OfficerRelationship.merge(a, b)
        elif AssociatedRole(a.associated_role).is_shareholder():
            return ShareholderRelationship.merge(a, b)
        else:
            return Relationship(
                {
                    "relationship_type": a.relationship_type,
                    "associated_role": a.associated_role,
                }
            )

    @classmethod
    def dedup(cls, relationships):
        keyed_by_kind = defaultdict(list)

        for relationship in relationships:
            keyed_by_kind[(
                relationship.relationship_type,
                relationship.associated_role,
                getattr(relationship, 'original_role', None)
            )].append(relationship)

        return [
            reduce(Relationship.merge, same_kind)
            for same_kind in keyed_by_kind.values()
        ]


class OfficerRelationship(Relationship):
    original_role = StringType(default=None)
    appointed_on = DateType(default=None)
    resigned_on = DateType(default=None)

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("relationship_type") == RelationshipType.OFFICER.value

    @classmethod
    def merge(cls, a, b):
        assert(a.relationship_type == b.relationship_type)
        assert(a.associated_role == b.associated_role)
        assert(a.original_role == b.original_role)

        return OfficerRelationship({
            'relationship_type': a.relationship_type,
            'associated_role': a.associated_role,
            'original_role': a.original_role,
            'appointed_on': a.appointed_on or b.appointed_on,
            'resigned_on': a.resigned_on or b.resigned_on,
        })


class ShareholderRelationship(Relationship):
    shareholdings = ListType(ModelType(Shareholding), default=list, required=True)

    @serializable
    def total_percentage(self):
        from decimal import Decimal
        return float(sum(Decimal(x.percentage) for x in self.shareholdings if x.percentage is not None))

    @classmethod
    def _claim_polymorphic(cls, data):
        return data.get("relationship_type") == RelationshipType.SHAREHOLDER.value

    def from_bvd_beneficial_owner(index, bvd_data):
        return ShareholderRelationship({
            "relationship_type": RelationshipType.SHAREHOLDER.value,
            "associated_role": AssociatedRole.BENEFICIAL_OWNER.value,
            "shareholdings": [],
        })

    def from_bvd_shareholder(index, bvd_data):
        return ShareholderRelationship({
            "relationship_type": RelationshipType.SHAREHOLDER.value,
            "associated_role": AssociatedRole.BENEFICIAL_OWNER.value,
            "shareholdings": [
                Shareholding.from_bvd(bvd_data.shareholder_direct_percentage[index])
            ],
        })

    @classmethod
    def merge(cls, a, b):
        assert(a.relationship_type == b.relationship_type)
        assert(a.associated_role == b.associated_role)
        return ShareholderRelationship(
            {
                "relationship_type": a.relationship_type,
                "associated_role": a.associated_role,
                "shareholdings": a.shareholdings + b.shareholdings
            }
        )


class Associate(BaseModel):
    associate_id = UUIDType(required=True)
    merge_id = UUIDType(export_level=DROP)
    entity_type = StringType(choices=[ty.value for ty in EntityType], required=True)
    immediate_data = ModelType(AssociateEntityData, required=True)
    relationships = ListType(ModelType(Relationship), required=True)

    def from_bvd_shareholder(index, bvd_data, bvd_ids):
        entity_type = (
            EntityType.INDIVIDUAL
            if bvd_data.shareholder_is_individual(index)
            else EntityType.COMPANY
        )

        merge_id = bvd_data.shareholder_merge_id(index)
        bvd_id = bvd_data.shareholder_bvd_id[index]
        if bvd_id is not None:
            bvd_ids[merge_id] = bvd_id

        return Associate(
            {
                "merge_id": merge_id,
                "entity_type": entity_type.value,
                "immediate_data": AssociateEntityData.from_bvd_shareholder(
                    entity_type, index, bvd_data
                ),
                "relationships": [Relationship.from_bvd_shareholder(index, bvd_data)],
            }
        )

    def from_bvd_beneficial_owner(index, bvd_data, bvd_ids):
        merge_id = bvd_data.beneficial_owner_merge_id(index)
        bvd_id = bvd_data.beneficial_owner_bvd_id[index]
        if bvd_id is not None:
            bvd_ids[merge_id] = bvd_id

        return Associate(
            {
                "merge_id": merge_id,
                # UBOs are always individuals
                "entity_type": EntityType.INDIVIDUAL.value,
                "immediate_data": AssociateEntityData.from_bvd_beneficial_owner(
                    index, bvd_data
                ),
                "relationships": [
                    Relationship.from_bvd_beneficial_owner(index, bvd_data),
                ],
            }
        )

    def from_bvd_contacts(index, bvd_data, bvd_ids):
        entity_type = EntityType.from_bvd_officer(index, bvd_data)
        relationship = Relationship.from_bvd_contacts(index, bvd_data)
        if relationship is None:
            return None

        merge_id = bvd_data.contact_merge_id(index)
        bvd_id = bvd_data.contact_bvd_id[index]
        if bvd_id is not None:
            bvd_ids[merge_id] = bvd_id

        return Associate(
            {
                "merge_id": merge_id,
                "entity_type": entity_type.value,
                "immediate_data": AssociateEntityData.from_bvd_officer(
                    entity_type, index, bvd_data
                ),
                "relationships": [relationship],
            }
        )

    @classmethod
    def merge(cls, bvd_ids, a, b):
        assert(a.merge_id == b.merge_id)

        bvd_id = bvd_ids.get(a.merge_id, None)
        if bvd_id:
            associate_id = build_resolver_id(bvd_id)
        else:
            associate_id = a.merge_id

        return Associate(
            {
                "associate_id": associate_id,
                "merge_id": a.merge_id,
                "entity_type": a.entity_type,
                "immediate_data": AssociateEntityData.merge(
                    a.immediate_data, b.immediate_data
                ),
                "relationships": Relationship.dedup(a.relationships + b.relationships),  # todo merge relationships
            }
        )


def merge_associates_by_id(bvd_ids, associates):
    keyed_by_id = defaultdict(list)

    for associate in associates:
        keyed_by_id[associate.merge_id].append(associate)

    return [
        reduce(
            partial(Associate.merge, bvd_ids),
            matching_associates,
            matching_associates[0]
        )
        for matching_associates in keyed_by_id.values()
    ]


class CompanyData(BaseModel):
    metadata = ModelType(CompanyMetadata, required=True)
    associated_entities = ListType(ModelType(Associate), required=True)

    def from_bvd(bvd_data):
        bvd_ids = {}
        shareholders = [
            Associate.from_bvd_shareholder(index, bvd_data, bvd_ids)
            for index in range(0, bvd_data.num_shareholders)
        ]
        beneficial_owners = [
            Associate.from_bvd_beneficial_owner(index, bvd_data, bvd_ids)
            for index in range(0, bvd_data.num_beneficial_owners)
        ]

        officers = [
            officer
            for officer in (
                Associate.from_bvd_contacts(index, bvd_data, bvd_ids)
                for index in range(0, bvd_data.num_contacts)
            )
            if officer
        ]

        return CompanyData(
            {
                "metadata": CompanyMetadata.from_bvd(bvd_data),
                "associated_entities": merge_associates_by_id(
                    bvd_ids,
                    shareholders + beneficial_owners + officers
                ),
            }
        )


class CompanyDataCheckResponse(BaseModel):
    output_data = ModelType(CompanyData, serialize_when_none=True)
    errors = ListType(ModelType(Error), serialize_when_none=True, default=list)
    price = IntType()
    raw = BaseType()
