from typing import Union, Optional, List
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from datetime import date

from passfort.individual_data import IndividualData, Address as PassFortAddress
from passfort.company_data import CompanyData
from passfort.cifas_check import CifasConfig
from passfort.date import DatePrecision


@dataclass
class StructuredAddress:
    HouseNumber: Optional[str]
    HouseName: Optional[str]
    FlatOrUnit: Optional[str]
    Street: Optional[str]
    Town: Optional[str]
    District: Optional[str]
    Postcode: Optional[str]

    @staticmethod
    def encode(address):
        return {
            'Address': address,
        }

    @classmethod
    def from_passfort_address(cls, address: PassFortAddress) -> 'StructuredAddress':
        town_and_locality = address.locality and address.postal_town
        return cls(
            HouseNumber=address.street_number,
            HouseName=address.premise,
            FlatOrUnit=address.subpremise,
            Street=address.route,
            Town=address.locality or address.postal_town,
            District=address.postal_town if town_and_locality else None,
            Postcode=address.postal_code,
        )


@dataclass
class IndividualParty:
    Surname: Optional[str]
    FirstName: Optional[str]
    MiddleNames: Optional[str]
    """CIFAS only accepts full dates"""
    BirthDate: Optional[date] = field(metadata=config(encoder=date.isoformat))
    Address: StructuredAddress = field(metadata=config(encoder=StructuredAddress.encode))
    EmailAddress: Optional[str] = None
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

    @classmethod
    def from_passfort_data(
            cls,
            entity_data: Union[IndividualData, CompanyData],
            config: CifasConfig,
    ) -> 'FullSearchRequest':
        # @TODO generate short id for member references
        return cls(
            Product=config.product_code,
            SearchType=config.search_type,
            MemberSearchReference='REPLACEMEWITHAGENERATEDID',
            Party=create_party_from_passfort_data(entity_data),
        )

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


def create_party_from_passfort_data(entity_data: Union[IndividualData, CompanyData]) -> Union[IndividualParty, CompanyParty]:
    if isinstance(entity_data, IndividualData):
        address_history = entity_data.address_history
        personal_details = entity_data.personal_details
        full_name = personal_details.name

        first_name = None
        middle_names: List[str] = []
        if full_name.given_names:
            first_name, *middle_names = full_name.given_names

        if address_history:
            address_history_item, *_ = address_history
            address = address_history_item.address
        else:
            address = PassFortAddress()

        return IndividualParty(
            Surname=full_name.family_name,
            FirstName=first_name,
            MiddleNames=' '.join(middle_names) if middle_names else None,
            BirthDate=personal_details.dob.value if personal_details.dob.precision == DatePrecision.YEAR_MONTH_DAY else None,
            Address=StructuredAddress.from_passfort_address(address),
        )

    raise NotImplemented()
