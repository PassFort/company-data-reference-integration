from typing import Union, List, Dict, Optional
from enum import Enum
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from passfort import EntityType, union_list
from passfort.date import PartialDate
from passfort.address import AddressHistoryItem, Address


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
