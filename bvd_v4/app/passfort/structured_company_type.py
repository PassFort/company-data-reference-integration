from enum import Enum
import logging

from schematics.types import BooleanType, StringType

from app.passfort.base_model import BaseModel


class OwnershipType(Enum):
    PARTNERSHIP = 'PARTNERSHIP'
    COMPANY = 'COMPANY'
    ASSOCIATION = 'ASSOCIATION'
    SOLE_PROPRIETORSHIP = 'SOLE_PROPRIETORSHIP'
    TRUST = 'TRUST'
    OTHER = 'OTHER'


class StructuredCompanyType(BaseModel):
    ownership_type = StringType(choices=list(OwnershipType))
    is_public = BooleanType()
    is_limited = BooleanType()

    def from_bvd(standardised_legal_form):
        if standardised_legal_form is None:
            return standardised_legal_form
        try:
            structured_company_type = STRUCTURED_COMPANY_TYPE_MAP[standardised_legal_form.lower()]
            return structured_company_type
        except Exception:
            logging.error(f'Unrecognised company type {standardised_legal_form}')

        return None


STRUCTURED_COMPANY_TYPE_MAP = {
    'public limited companies': StructuredCompanyType({
        'is_public': True,
        'is_limited': True,
        'ownership_type': OwnershipType.COMPANY.value
    }),
    'private limited companies': StructuredCompanyType({
        'is_public': False,
        'is_limited': True,
        'ownership_type': OwnershipType.COMPANY.value
    }),
    'partnerships': StructuredCompanyType({'ownership_type': OwnershipType.PARTNERSHIP.value}),
    'sole traders/proprietorships': StructuredCompanyType({'ownership_type': OwnershipType.SOLE_PROPRIETORSHIP.value}),
    'public authorities': StructuredCompanyType({'is_public': True, 'ownership_type': OwnershipType.OTHER.value}),
    'non profit organisations': StructuredCompanyType({'ownership_type': OwnershipType.ASSOCIATION.value}),
    'branches': StructuredCompanyType({'ownership_type': OwnershipType.OTHER.value}),
    'foreign companies': StructuredCompanyType({'ownership_type': OwnershipType.COMPANY.value}),
    'other legal forms': StructuredCompanyType({'ownership_type': OwnershipType.OTHER.value}),
    'companies with unknown/unrecorded legal form': StructuredCompanyType({'ownership_type': OwnershipType.OTHER.value})
}
