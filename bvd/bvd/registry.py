from typing import Optional, List, cast
from enum import Enum
from datetime import datetime

from bvd.utils import BvDServiceException, CompanyRawData, send_sentry_exception
from bvd.format_utils import BaseObject, EntityType, format_date
from bvd.officers import format_officers, Officers


UNLISTED_ISIN = 'Unlisted'
ADDRESS_FIELDS = ('ADDR', 'ADDR1', 'ADDR2', 'ADDR3', 'ADDR4', 'POSTCODE', 'CITY', 'COUNTRY')
COMPANY_IDENTIFIERS_MAP = {
    'bvd_id': 'BVDID',
    'bvd9': 'BVD9',
    'isin': 'ISIN',
    'lei': 'LEI',
    'number': 'TRADEREGISTERNR',
}


class TaxIdType(Enum):
    EUROVAT = "EUROVAT"
    VAT = "VAT"
    EIN = "EIN"


class TaxId(BaseObject):
    tax_id_type: TaxIdType
    value: str


COMPANY_TAX_IDENTIFIERS_MAP = {
    TaxIdType.EIN: 'IRS',
    TaxIdType.VAT: 'VATNUMBER',
    TaxIdType.EUROVAT: 'EUROVAT',
}


class CompanyTypeError(Exception):
    pass

    def to_dict(self):
        return {'message': self.args[0]}


class OwnershipType(Enum):
    PARTNERSHIP = 'PARTNERSHIP'
    COMPANY = 'COMPANY'
    ASSOCIATION = 'ASSOCIATION'
    SOLE_PROPRIETORSHIP = 'SOLE_PROPRIETORSHIP'
    TRUST = 'TRUST'
    OTHER = 'OTHER'


class StructuredCompanyType(BaseObject):
    ownership_type: Optional[OwnershipType]
    is_public: Optional[bool]
    is_limited: Optional[bool]

    def __init__(self, d={}) -> None:
        self.__dict__ = {**self.__dict__, **d}


STRUCTURED_COMPANY_TYPE_MAP = {
    'public limited companies': StructuredCompanyType({
        'is_public': True,
        'is_limited': True,
        'ownership_type': OwnershipType.COMPANY
    }),
    'private limited companies': StructuredCompanyType({
        'is_public': False,
        'is_limited': True,
        'ownership_type': OwnershipType.COMPANY
    }),
    'partnerships': StructuredCompanyType({'ownership_type': OwnershipType.PARTNERSHIP}),
    'sole traders/proprietorships': StructuredCompanyType({'ownership_type': OwnershipType.SOLE_PROPRIETORSHIP}),
    'public authorities': StructuredCompanyType({'is_public': True, 'ownership_type': OwnershipType.OTHER}),
    'non profit organisations': StructuredCompanyType({'ownership_type': OwnershipType.ASSOCIATION}),
    'branches': StructuredCompanyType({'ownership_type': OwnershipType.OTHER}),
    'foreign companies': StructuredCompanyType({'ownership_type': OwnershipType.COMPANY}),
    'other legal forms': StructuredCompanyType({'ownership_type': OwnershipType.OTHER}),
    'companies with unknown/unrecorded legal form': StructuredCompanyType({'ownership_type': OwnershipType.OTHER})
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


def format_previous_names(raw_data: CompanyRawData) -> List[PreviousName]:
    # PREVNAME: Previous company name; NAMECHDT: Company name change date
    # If data is missing we get None
    name: Optional[str] = raw_data.get('PREVNAME')
    end_date: Optional[str] = raw_data.get('NAMECHDT')

    if name is not None:
        end = format_date(end_date)
        return [PreviousName(name, end)]

    return []


def format_company_type(raw_data: CompanyRawData) -> Optional[str]:
    return raw_data.get('SLEGALF')


def format_structured_company_type(raw_data: CompanyRawData) -> Optional[StructuredCompanyType]:
    company_type = raw_data.get('SLEGALF')
    if company_type is not None:
        try:
            structured_company_type = STRUCTURED_COMPANY_TYPE_MAP[company_type.lower()]
            return structured_company_type
        except Exception:
            exc = CompanyTypeError(f'Unrecognised company type {company_type}')
            send_sentry_exception(exc, custom_data={'company_type': company_type})
            return StructuredCompanyType()
    return None


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
    return ','.join(cast(str, raw_data[field]) for field in ADDRESS_FIELDS if raw_data.get(field) is not None)


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
    isin: Optional[str]
    lei: str
    tax_ids: List[TaxId]
    name: Optional[str]
    company_type: Optional[str]
    structured_company_type: Optional[StructuredCompanyType]
    incorporation_date: Optional[datetime]
    previous_names: List[PreviousName]
    sic_codes: List[SICCode]
    contact_information: ContactDetails
    freeform_address: str
    is_active: Optional[bool]

    @staticmethod
    def from_raw_data(raw_data: CompanyRawData) -> 'CompanyMetadata':
        metadata = CompanyMetadata()

        for dest_key, original_key in COMPANY_IDENTIFIERS_MAP.items():
            setattr(metadata, dest_key, raw_data.get(original_key))

        tax_ids = []
        for tax_id_type, original_key in COMPANY_TAX_IDENTIFIERS_MAP.items():
            value = raw_data.get(original_key)
            if value is not None:
                tax_id = TaxId()
                tax_id.tax_id_type = tax_id_type
                tax_id.value = value
                tax_ids.append(tax_id)
        metadata.tax_ids = tax_ids

        if metadata.isin == UNLISTED_ISIN:
            metadata.isin = None

        metadata.name = raw_data.get('NAME')
        metadata.company_type = format_company_type(raw_data)
        metadata.structured_company_type = format_structured_company_type(raw_data)
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
