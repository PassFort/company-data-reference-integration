from typing import Union, Optional, List
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from datetime import date
from uuid import uuid4

from passfort.individual_data import IndividualData, UKBankAccount, Address as PassFortAddress
from passfort.company_data import CompanyData
from passfort.cifas_check import CifasConfig, OutputData
from passfort.fraud_detection import FraudDetection
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
    """CIFAS only accepts full dates"""
    BirthDate: Optional[date] = field(metadata=config(encoder=date.isoformat))
    Address: StructuredAddress = field(metadata=config(encoder=StructuredAddress.encode))
    EmailAddress: Optional[str]
    HomeTelephone: Optional[str]
    NationalInsuranceNumber: Optional[str]
    Relevance: Optional[str] = 'APP'
    PartySequence: Optional[int] = 1


@dataclass
class CompanyParty:
    CompanyName: Optional[str]
    CompanyNumber: Optional[str]
    Relevance: str = 'APP'
    PartySequence: int = 1


@dataclass
class BankAccountDetails:
    SortCode: str
    AccountNumber: str


@dataclass
class FinancialDetails:
    BankAccount: BankAccountDetails


@dataclass_json
@dataclass
class FullSearchRequest:
    Product: str
    SearchType: str
    MemberSearchReference: str
    Party: Union[IndividualParty, CompanyParty]
    Finance: List[FinancialDetails]

    @classmethod
    def from_passfort_data(
            cls,
            entity_data: Union[IndividualData, CompanyData],
            config: CifasConfig,
    ) -> 'FullSearchRequest':
        finance_items: List[FinancialDetails] = []
        if isinstance(entity_data, IndividualData):
            if entity_data.banking_details:
                finance_items = [
                    FinancialDetails(
                        BankAccount=BankAccountDetails(
                            SortCode=bank_account.sort_code,
                            AccountNumber=bank_account.account_number,
                        ),
                    ) for bank_account in entity_data.banking_details.bank_accounts
                    if isinstance(bank_account, UKBankAccount)
                ]

        return cls(
            Product=config.product_code,
            SearchType=config.search_type,
            MemberSearchReference=str(uuid4())[:16],
            Party=create_party_from_passfort_data(entity_data),
            Finance=finance_items,
        )

    def to_dict(self) -> dict:
        ...


@dataclass_json
@dataclass
class FullSearchResultItem:
    # Data under this object is currently unused by the integration
    ...


@dataclass_json
@dataclass
class FullSearchResponse:
    MemberSearchReference: str
    FINDsearchReference: int
    FullSearchResult: List[FullSearchResultItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: Mapping) -> 'FullSearchResponse':
        ...

    def to_passfort_output_data(self):
        return OutputData(
            fraud_detection=FraudDetection(
                search_reference=str(self.FINDsearchReference),
                match_count=len(self.FullSearchResult),
            ),
        )


def create_party_from_passfort_data(entity_data: Union[IndividualData, CompanyData]) -> Union[IndividualParty, CompanyParty]:
    if isinstance(entity_data, IndividualData):
        address_history = entity_data.address_history
        personal_details = entity_data.personal_details
        contact_details = entity_data.contact_details
        full_name = personal_details.name
        national_identity_number = personal_details.national_identity_number

        first_name = None
        middle_names: List[str] = []
        if full_name.given_names:
            # There is no field for middle names on the party type
            first_name, *_middle_names = full_name.given_names

        if address_history:
            address_history_item, *_ = address_history
            address = address_history_item.address
        else:
            address = PassFortAddress()

        return IndividualParty(
            Surname=full_name.family_name,
            FirstName=first_name,
            BirthDate=personal_details.dob.value if personal_details.dob.precision == DatePrecision.YEAR_MONTH_DAY else None,
            Address=StructuredAddress.from_passfort_address(address),
            EmailAddress=contact_details.email if contact_details else None,
            HomeTelephone=contact_details.phone_number if contact_details else None,
            NationalInsuranceNumber=national_identity_number.get('GBR') if national_identity_number else None,
        )

    raise NotImplemented()
