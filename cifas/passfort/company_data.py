from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from passfort import EntityType
from passfort.address import AddressHistoryItem


@dataclass
class CompanyContactDetails:
    phone_number: Optional[str]
    email: Optional[str]


@dataclass
class CompanyMetadata:
    number: str
    name: str
    contact_details: Optional[CompanyContactDetails]


@dataclass_json
@dataclass
class CompanyData:
    metadata: CompanyMetadata
    addresses: List[AddressHistoryItem]
    entity_type: EntityType = EntityType.COMPANY
