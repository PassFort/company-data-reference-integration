from dataclasses import dataclass
from passfort import EntityType


@dataclass
class CompanyData:
    entity_type: EntityType = EntityType.COMPANY
