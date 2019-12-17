from dataclasses import dataclass
from dataclasses_json import dataclass_json
from passfort import EntityType


@dataclass_json
@dataclass
class CompanyData:
    entity_type: EntityType = EntityType.COMPANY
