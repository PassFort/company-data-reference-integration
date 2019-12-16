from typing import Union, List, Dict, Optional
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
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
    street_number: Optional[str] = None
    premise: Optional[str] = None
    subpremise: Optional[str] = None
    route: Optional[str] = None
    locality: Optional[str] = None
    postal_town: Optional[str] = None
    postal_code: Optional[str] = None
    country: Optional[str] = None


@dataclass
class AddressHistoryItem:
    address: Address


@dataclass
class ContactDetails:
    phone_number: Optional[str]
    email: Optional[str]


@dataclass
class BankAccount:
    type: str


@dataclass
class UKBankAccount:
    sort_code: str
    account_number: str
    country: str
    type: str = 'UK_ACCOUNT'


@dataclass
class BankingDetails:
    bank_accounts: List[Union[UKBankAccount, BankAccount]]


@dataclass_json
@dataclass
class IndividualData:
    personal_details: PersonalDetails
    address_history: List[AddressHistoryItem]
    contact_details: Optional[ContactDetails] = None
    banking_details: Optional[BankingDetails] = None
    entity_type: EntityType = EntityType.INDIVIDUAL
