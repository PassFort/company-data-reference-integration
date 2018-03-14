from typing import Optional, List
from enum import Enum
from datetime import datetime

from bvd.utils import CompanyRawData
from bvd.format_utils import BaseObject, EntityType, format_date
from bvd.officers import format_officers, Officers


UNLISTED_ISIN = 'Unlisted'
ADDRESS_FIELDS = ('ADDR', 'ADDR1', 'ADDR2', 'ADDR3', 'ADDR4', 'POSTCODE', 'CITY', 'COUNTRY')
COMPANY_IDENTIFIERS_MAP = {
    'bvd_id': 'BVDID',
    'bvd9': 'BVD9',
    'isin': 'ISIN',
    'irs': 'IRS',
    'vat_number': 'VATNUMBER',
    'eurovat_number': 'EUROVAT',
    'lei': 'LEI',
    'number': 'TRADEREGISTERNR',
}


class CompanyType(Enum):
    PLC = 'plc'
    LTD = 'ltd'
    LLP = 'llp'
    OTHER = 'other'


COMPANY_TYPE_MAP = {
    'public limited companies': CompanyType.PLC,
    'private limited companies': CompanyType.LTD,
    'partnerships': CompanyType.LLP,
    'sole traders/proprietorships': CompanyType.OTHER,
    'public authorities': CompanyType.OTHER,
    'non profit organisations': CompanyType.OTHER,
    'branches': CompanyType.OTHER,
    'foreign companies': CompanyType.OTHER,
    'other legal forms': CompanyType.OTHER,
    'companies with unknown/unrecorded legal form': CompanyType.OTHER,
}


class PreviousName(BaseObject):
    name: str
    end: Optional[datetime]

    def __init__(self, name: str, end: Optional[datetime]) -> None:
        self.name = name
        self.end = end


class SICCode(BaseObject):
    code: str
    description: str

    def __init__(self, code: str, description: str) -> None:
        self.code = code
        self.description = description


def format_previous_names(raw_data: CompanyRawData) -> Optional[List[PreviousName]]:
    # PREVNAME: Previous company name; NAMECHDT: Company name change date
    # If data is missing we get None
    name: Optional[str] = raw_data.get('PREVNAME')
    end_date: Optional[str] = raw_data.get('NAMECHDT')

    if name is not None:
        end = format_date(end_date)
        return [PreviousName(name, end)]

    return None


def format_company_type(raw_data: CompanyRawData) -> CompanyType:
    # SLEGALF: Company type;
    company_type = raw_data['SLEGALF']
    try:
        return COMPANY_TYPE_MAP[company_type.lower()]
    except (ValueError, KeyError):
        pass

    return CompanyType.OTHER


def format_sic_codes(raw_data: CompanyRawData) -> Optional[List[SICCode]]:
    # NATPCOD: Primary code in national industry classification
    # NATPDES: Primary code (text description)
    # If data is missing we get None
    # There is only one sic_code per company

    code: Optional[str] = raw_data.get('NATPCOD')
    description: Optional[str] = raw_data.get('NATPDES')
    if code and description:
        return [SICCode(code, description)]

    return None


def format_current_status(raw_data: CompanyRawData) -> Optional[str]:
    # TODO: Handle dormant companies
    status: Optional[str] = raw_data.get('HISTORIC_STATUS_STR')
    return status


def format_is_active(raw_data: CompanyRawData) -> Optional[bool]:
    status = format_current_status(raw_data)
    if status:
        return status.startswith('Active')

    return None


def format_address(raw_data: CompanyRawData) -> str:
    return ','.join(raw_data[field] for field in ADDRESS_FIELDS if raw_data.get(field) is not None)


class ContactDetails(BaseObject):
    url: Optional[str]
    phone_number: Optional[str]
    email: Optional[str]

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'ContactDetails':
        info = ContactDetails()
        info.url = raw_data.get('WEBSITE')
        info.phone_number = raw_data.get('PHONE')
        info.email = raw_data.get('EMAIL')
        return info


class CompanyMetadata(BaseObject):
    bvd_id: str
    number: str
    bvd9: str
    isin: str
    irs: str
    vat_number: str
    eurovat_number: str
    lei: str
    name: str
    company_type: CompanyType
    incorporation_date: datetime
    previous_names: List[PreviousName]
    sic_codes: List[SICCode]
    contact_information: ContactDetails
    freeform_address: str
    is_active: bool

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'CompanyMetadata':
        metadata = CompanyMetadata()

        for dest_key, original_key in COMPANY_IDENTIFIERS_MAP.items():
            setattr(metadata, dest_key, raw_data.get(original_key))

        if metadata.isin == UNLISTED_ISIN:
            metadata.isin = None

        metadata.name = raw_data.get('NAME')
        metadata.company_type = format_company_type(raw_data)
        metadata.is_active = format_is_active(raw_data)
        metadata.incorporation_date = format_date(raw_data.get('DATEINC'))
        metadata.previous_names = format_previous_names(raw_data)
        metadata.freeform_address = format_address(raw_data)
        return metadata


class CompanyData(BaseObject):
    entity_type: EntityType
    metadata: CompanyMetadata
    officers: Officers

    def __init__(self):
        self.entity_type = EntityType.COMPANY

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'CompanyData':
        data = CompanyData()
        data.metadata = CompanyMetadata.from_raw_data(raw_data)
        data.officers = format_officers(raw_data)
        return data


def format_registry_data(raw_data: CompanyRawData) -> CompanyData:
    return CompanyData.from_raw_data(raw_data)
