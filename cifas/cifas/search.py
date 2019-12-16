from typing import Union, Optional
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from datetime import date
from passfort.date import PartialDate


@dataclass
class StructuredAddress:
    HouseNumber: Optional[str]
    Postcode: Optional[str]

    @staticmethod
    def encode(address):
        return {
            'Address': address,
        }


@dataclass
class IndividualParty:
    Surname: Optional[str]
    FirstName: Optional[str]
    """CIFAS only accepts full dates"""
    BirthDate: Optional[date] = field(metadata=config(encoder=date.isoformat))
    EmailAddress: Optional[str]
    Address: StructuredAddress = field(metadata=config(encoder=StructuredAddress.encode))
    Relevance: Optional[str] = 'APP'
    PartySequence: Optional[int] = 1


@dataclass
class CompanyParty:
    CompanyName: Optional[str]
    CompanyNumber: Optional[str]
    Relevance: str = 'APP'
    PartySequence: int = 1


@dataclass_json
@dataclass
class FullSearchRequest:
    Product: str
    SearchType: str
    MemberSearchReference: str
    Party: Union[IndividualParty, CompanyParty]

    def to_dict(self) -> dict:
        ...


@dataclass_json
@dataclass
class FullSearchResponse:
    MemberSearchReference: str
    FINDsearchReference: int

    @classmethod
    def from_dict(cls, value: Mapping) -> 'FullSearchResponse':
        ...
