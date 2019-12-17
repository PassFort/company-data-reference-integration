from typing import Union, List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from passfort import EntityType, union_list
from passfort.date import PartialDate


@dataclass
class FullName:
    given_names: Optional[List[str]]
    family_name: Optional[str]


@dataclass
class PersonalDetails:
    name: FullName
    dob: Optional[PartialDate] = field(
        metadata=config(
            decoder=PartialDate.decode,
        ), 
        default_factory=type(None),
    )
    national_identity_number: Optional[Dict[str, str]] = None


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


class BankAccountType(Enum):
    UK_ACCOUNT = 'UK_ACCOUNT'


@dataclass_json
@dataclass
class UKBankAccount:
    sort_code: str
    account_number: str
    type: BankAccountType = BankAccountType.UK_ACCOUNT


@dataclass
class BankingDetails:
    bank_accounts: List[Union[UKBankAccount, dict]] = union_list(
        UKBankAccount,
        unknown_type=dict,
    )


@dataclass_json
@dataclass
class IndividualData:
    personal_details: PersonalDetails
    address_history: List[AddressHistoryItem]
    contact_details: Optional[ContactDetails] = None
    banking_details: Optional[BankingDetails] = None
    entity_type: EntityType = EntityType.INDIVIDUAL
