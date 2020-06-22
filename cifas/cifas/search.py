from typing import Union, Optional, List
from collections.abc import Mapping
from dataclasses import dataclass, field
from dataclasses_json import dataclass_json, config
from datetime import date
from uuid import uuid4

from cifas.codes import Product, FilingReason, CaseType, Member
from passfort.individual_data import IndividualData, UKBankAccount, Address as PassFortAddress
from passfort.company_data import CompanyData
from passfort.cifas_check import CifasConfig, OutputData
from passfort.fraud_detection import FraudDetection, FraudCase, DatabaseType
from passfort.date import DatePrecision


@dataclass
class StructuredAddress:
    HouseNumber: Optional[str] = None
    HouseName: Optional[str] = None
    FlatOrUnit: Optional[str] = None
    Street: Optional[str] = None
    Town: Optional[str] = None
    District: Optional[str] = None
    Postcode: Optional[str] = None

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
class BankAccountDetails:
    SortCode: str
    AccountNumber: str

    def __post_init__(self):
        sort_code = self.SortCode
        if sort_code:
            self.SortCode = sort_code.replace('-', '')


@dataclass
class FinancialDetails:
    BankAccount: BankAccountDetails


@dataclass
class IndividualParty:
    Surname: Optional[str]
    FirstName: Optional[str]
    BirthDate: Optional[date] = field(
        metadata=config(
            encoder=lambda value: value and date.isoformat(value)
        )
    )
    Address: List[StructuredAddress] = field(
        metadata=config(
            encoder=lambda value: [StructuredAddress.encode(item) for item in value],
        ),
    )
    EmailAddress: Optional[str] = None
    HomeTelephone: Optional[str] = None
    Finance: Optional[List[FinancialDetails]] = None
    NationalInsuranceNumber: Optional[str] = None
    Relevance: Optional[str] = 'APP'
    PartySequence: Optional[int] = 1


@dataclass
class CompanyParty:
    CompanyName: Optional[str]
    CompanyNumber: Optional[str]
    CompanyTelephone: Optional[str]
    EmailAddress: Optional[str]
    Address: List[StructuredAddress] = field(
        metadata=config(
            encoder=lambda value: [StructuredAddress.encode(item) for item in value],
        ),
    )
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
        return cls(
            Product=config.product_code,
            SearchType=config.search_type,
            MemberSearchReference=str(uuid4())[:16],
            Party=create_party_from_passfort_data(entity_data),
        )

    def to_dict(self) -> dict:
        ...


@dataclass_json
@dataclass
class BasicCaseDetail:
    CaseId: int
    OwningMember: int
    ManagingMember: int
    CaseType: str
    Product: str
    DoNotFilter: bool
    SupplyDate: Optional[date]
    ApplicationDate: Optional[date]
    ClaimDate: Optional[date]


@dataclass_json
@dataclass
class FullCaseDetail:
    BasicCaseDetail: BasicCaseDetail
    FilingReason: List[str]
    DeliveryChannel: Optional[str]
    IPAddress: Optional[str]
    Facility: Optional[str]
    LinkedCasesCount: int


@dataclass_json
@dataclass
class FullSearchResultItem:
    FullCaseDetail: FullCaseDetail

    def convert_code(self, cached_codes, get_codes, code_name, k):
        try:
            return cached_codes[k].value
        except KeyError:
            return get_codes(code_name)[k]

    def to_passfort_output_data(self, get_codes):
        reporting_company = self.convert_code(Member, get_codes, 'MEMBER',
                                              str(self.FullCaseDetail.BasicCaseDetail.OwningMember))
        case_type = self.convert_code(CaseType, get_codes, 'CASTYP', self.FullCaseDetail.BasicCaseDetail.CaseType)
        product = self.convert_code(Product, get_codes, 'PRODCT', self.FullCaseDetail.BasicCaseDetail.Product)
        filing_reason = [self.convert_code(FilingReason, get_codes, 'FILREA', fr) for fr in self.FullCaseDetail.FilingReason]

        return FraudCase(
            id=str(self.FullCaseDetail.BasicCaseDetail.CaseId),
            reporting_company=reporting_company,
            case_type=case_type,
            product=product,
            do_not_filter=self.FullCaseDetail.BasicCaseDetail.DoNotFilter,
            supply_date=self.FullCaseDetail.BasicCaseDetail.SupplyDate,
            application_date=self.FullCaseDetail.BasicCaseDetail.ApplicationDate,
            claim_date=self.FullCaseDetail.BasicCaseDetail.ClaimDate,
            filing_reason=filing_reason,
            database_type=DatabaseType.CIFAS,
        )


@dataclass_json
@dataclass
class FullSearchResponse:
    MemberSearchReference: str
    FINDsearchReference: int
    FullSearchResult: List[FullSearchResultItem] = field(default_factory=list)

    @classmethod
    def from_dict(cls, value: Mapping) -> 'FullSearchResponse':
        ...

    def to_passfort_output_data(self, members):
        return OutputData(
            fraud_detection=FraudDetection(
                search_reference=str(self.FINDsearchReference),
                match_count=len(self.FullSearchResult),
                matches=[i.to_passfort_output_data(members) for i in self.FullSearchResult]
            ),
        )


def create_party_from_passfort_data(entity_data: Union[IndividualData, CompanyData]) -> Union[IndividualParty, CompanyParty]:
    if isinstance(entity_data, IndividualData):
        address_history = entity_data.address_history or []
        personal_details = entity_data.personal_details
        contact_details = entity_data.contact_details
        full_name = personal_details.name
        national_identity_number = personal_details.national_identity_number

        first_name = None
        middle_names: List[str] = []
        if full_name.given_names:
            # There is no field for middle names on the party type
            first_name, *_middle_names = full_name.given_names

        finance_items: List[FinancialDetails] = []
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

        return IndividualParty(
            Surname=full_name.family_name,
            FirstName=first_name,

            # Cifas does not accept partial dates
            BirthDate=personal_details.dob.value if personal_details.dob and
            personal_details.dob.precision == DatePrecision.YEAR_MONTH_DAY else None,

            Address=[
                StructuredAddress.from_passfort_address(item.address)
                # Cifas API accepts 10 addresses max
                for item in address_history[:10]
            ],
            EmailAddress=contact_details.email if contact_details else None,
            HomeTelephone=contact_details.phone_number if contact_details else None,
            NationalInsuranceNumber=national_identity_number.get('GBR') if national_identity_number else None,
            Finance=finance_items,
        )
    return CompanyParty(
        CompanyName=entity_data.metadata.name,
        CompanyNumber=entity_data.metadata.number,
        CompanyTelephone=entity_data.metadata.contact_details.phone_number if entity_data.metadata and
        entity_data.metadata.contact_details else None,
        EmailAddress=entity_data.metadata.contact_details.email if entity_data.metadata and
        entity_data.metadata.contact_details else None,
        Address=[
            StructuredAddress.from_passfort_address(item.address)
            # Cifas API accepts 10 addresses max
            for item in (entity_data.metadata.addresses or [])[:10]
        ],
    )
