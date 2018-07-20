from typing import List

from bvd.format_utils import BaseObject, EntityType, format_date
from bvd.utils import CompanyRawData
from bvd.registry import CompanyMetadata, format_company_type, format_structured_company_type
from bvd.shareholders import Shareholder, format_shareholders
from bvd.beneficial_owners import BeneficialOwner, format_beneficial_owners


class OwnershipStructure(BaseObject):
    shareholders: List[Shareholder]
    beneficial_owners: List[BeneficialOwner]

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'OwnershipStructure':
        ownership_structure = OwnershipStructure()
        ownership_structure.shareholders = format_shareholders(raw_data)
        ownership_structure.beneficial_owners = format_beneficial_owners(raw_data)
        return ownership_structure


class CompanyOwnershipData(BaseObject):
    entity_type: EntityType
    metadata: CompanyMetadata
    ownership_structure: OwnershipStructure

    def __init__(self):
        self.entity_type = EntityType.COMPANY

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'CompanyOwnershipData':
        ownership_data = CompanyOwnershipData()
        ownership_data.metadata = CompanyMetadata()
        ownership_data.metadata.company_type = format_company_type(raw_data)
        ownership_data.metadata.structured_company_type = format_structured_company_type(raw_data)
        ownership_data.ownership_structure = OwnershipStructure.from_raw_data(raw_data)
        return ownership_data


def format_ownership_data(raw_data: CompanyRawData) -> CompanyOwnershipData:
    return CompanyOwnershipData.from_raw_data(raw_data)
