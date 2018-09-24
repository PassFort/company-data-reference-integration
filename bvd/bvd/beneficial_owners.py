from typing import Optional, Dict, ItemsView, List, Tuple, cast
from datetime import datetime

from bvd.utils import CompanyRawData
from bvd.format_utils import BaseObject, EntityType, format_names, format_date
from bvd.officers import DATA_NOT_ACCESSIBLE


BENEFICIAL_OWNER_FIELD_MAP = {
    'full_name': 'BO_NAMEORIGINALLANGUAGE',
    'first_names': 'BO_FIRSTNAME',
    'last_name': 'BO_LASTNAME',
    'dob': 'BO_BIRTHDATE',
    'uci': 'BO_UPI',
    'bvd_id': 'BO_SUITEID',

}

BORawData = Dict[str, str]


def format_bo_names(type_: EntityType, raw_data: BORawData) -> Tuple[str, str]:
    return format_names(
        raw_data['first_names'],
        raw_data['last_name'],
        raw_data['full_name'],
        type_,
    )


class BeneficialOwner(BaseObject):
    bvd_id: str
    bvd_uci: str
    type: EntityType
    first_names: str
    last_name: str
    dob: Optional[datetime]

    @staticmethod
    def from_raw_data(raw_data: BORawData) -> 'BeneficialOwner':
        bo = BeneficialOwner()
        bo.bvd_id = raw_data['bvd_id']
        bo.bvd_uci = raw_data['uci']
        bo.type = EntityType.COMPANY if bo.bvd_uci is None else EntityType.INDIVIDUAL
        first_names, last_name = format_bo_names(bo.type, raw_data)
        bo.first_names = first_names
        bo.last_name = last_name
        bo.dob = format_date(raw_data['dob'])
        return bo


def format_benefical_owner(bos_data: ItemsView[str, list], idx: int) -> BeneficialOwner:
    bo_data: BORawData = {attr: value[idx] for attr, value in bos_data}
    return BeneficialOwner.from_raw_data(bo_data)


def format_beneficial_owners(raw_data: CompanyRawData) -> List[BeneficialOwner]:
    str_num_bo = raw_data.get('NrBeneficialOwners')
    num_bo = 0
    if str_num_bo and str_num_bo != DATA_NOT_ACCESSIBLE:
        num_bo = int(str_num_bo)

    if num_bo > 0:
        name_list = raw_data['BO_NAMEORIGINALLANGUAGE']
        num_bo = len(name_list) if name_list else 0

    bos_data = cast(ItemsView[str, list], {
        dest: raw_data.get(source, [''] * num_bo)
        for dest, source in BENEFICIAL_OWNER_FIELD_MAP.items()
    }.items())

    return [format_benefical_owner(bos_data, idx) for idx in range(num_bo)]
