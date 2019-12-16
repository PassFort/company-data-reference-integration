from typing import Union, List, Dict, Optional
from dataclasses import dataclass, field
from dataclasses_json import config
from passfort import EntityType
from passfort.date import PartialDate

@dataclass
class FullName:
    title: Optional[str]
    given_names: Optional[List[str]]
    family_name: Optional[str]


@dataclass
class PersonalDetails:
    name: FullName
    dob: PartialDate = field(metadata=config(decoder=PartialDate.decode))
    nationality: Optional[str]
    gender: Optional[str]
    national_identity_number: Dict[str, str]


@dataclass
class Address:
    street_number: Optional[str]
    premise: Optional[str]


@dataclass
class AddressHistoryItem:
    address: Address


@dataclass
class ContactDetails:
    phone_number: Optional[str]
    email: Optional[str]


@dataclass
class BankingDetails:
    bank_accounts: List[dict]


@dataclass
class IndividualData:
    personal_details: PersonalDetails
    address_history: List[AddressHistoryItem]
    contact_details: Optional[ContactDetails]
    banking_details: Optional[BankingDetails]
    entity_type: EntityType = EntityType.INDIVIDUAL
