from typing import List, Optional
from dataclasses import dataclass
from dataclasses_json import dataclass_json
from passfort import EntityType
from passfort.address import AddressHistoryItem


@dataclass
class CompanyContactDetails:
    phone_number: Optional[str] = None
    email: Optional[str] = None


@dataclass
class CompanyMetadata:
    number: str
    name: str
    addresses: List[AddressHistoryItem]
    contact_details: Optional[CompanyContactDetails] = None


@dataclass_json
@dataclass
class CompanyData:
    metadata: CompanyMetadata
    entity_type: EntityType = EntityType.COMPANY
