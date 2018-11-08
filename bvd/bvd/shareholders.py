from typing import List, Tuple, Dict, ItemsView, Optional, cast
from pycountry import countries

from bvd.utils import CompanyRawData
from bvd.format_utils import BaseObject, EntityType, format_names
from bvd.officers import DATA_NOT_ACCESSIBLE

INDIVIDUAL_TYPE = 'One or more named individuals or families'
SHAREHOLDER_FIELD_MAP = {
    'full_name': 'shareholder_full_names',
    'first_names': 'shareholder_first_names',
    'last_name': 'shareholder_last_names',
    'type': 'shareholder_types',
    'uci': 'shareholder_ucis',
    'direct': 'shareholder_direct_percentages',
    'total': 'shareholder_total_percentages',
    'country_code': 'shareholder_country_codes',
    'state_code': 'shareholder_state_codes',
    'bvd_id': 'shareholder_bvd_ids',
    'bvd9': 'shareholder_bvd9',
    'lei': 'shareholder_leis',
}


def format_country_code(raw_data: Dict[str, str]) -> Optional[str]:
    input_code = raw_data.get('country_code')
    try:
        return countries.get(alpha_2=input_code).alpha_3
    except KeyError:
        return None


def format_shareholders_names(type_: EntityType, raw_data: Dict[str, str]) -> Tuple[str, str]:
    return format_names(
        raw_data['first_names'],
        raw_data['last_name'],
        raw_data['full_name'],
        type_,
    )


def format_percentage(input_string: str) -> Optional[float]:
    try:
        return float(input_string) / 100
    except ValueError:
        return None


class Shareholding(BaseObject):
    percentage: Optional[float]

    def __init__(self, raw_data: Dict[str, str]) -> None:
        self.percentage = format_percentage(raw_data['direct'])


def format_shareholdings(raw_data: Dict[str, str]) -> List[Shareholding]:
    shareholding = Shareholding(raw_data)
    if shareholding.percentage is not None:
        return [shareholding]
    return []


class Shareholder(BaseObject):
    bvd_id: str
    bvd9: str
    bvd_uci: str
    lei: str
    type: EntityType
    country_of_incorporation: Optional[str]
    state_of_incorporation: str
    first_names: str
    last_name: str
    shareholdings: List[Shareholding]

    @staticmethod
    def from_raw_data(raw_data: Dict[str, str]) -> 'Shareholder':
        shareholder = Shareholder()
        shareholder.bvd_id = raw_data['bvd_id']
        shareholder.bvd9 = raw_data['bvd9']
        shareholder.bvd_uci = raw_data['uci']
        shareholder.lei = raw_data['lei']
        shareholder.type = EntityType.INDIVIDUAL if raw_data['type'] == INDIVIDUAL_TYPE else EntityType.COMPANY
        shareholder.country_of_incorporation = format_country_code(raw_data)
        shareholder.state_of_incorporation = raw_data['state_code']
        first_names, last_name = format_shareholders_names(shareholder.type, raw_data)
        shareholder.first_names = first_names
        shareholder.last_name = last_name
        shareholder.shareholdings = format_shareholdings(raw_data)
        return shareholder


def format_shareholder(shareholders_data: ItemsView[str, list], idx: int) -> Shareholder:
    shareholder_data: Dict[str, str] = {attr: value[idx] for attr, value in shareholders_data}
    return Shareholder.from_raw_data(shareholder_data)


def format_shareholders(raw_data: CompanyRawData) -> List[Shareholder]:
    str_num_shareholders = raw_data.get('num_shareholders')
    num_shareholders = 0
    if str_num_shareholders and str_num_shareholders != DATA_NOT_ACCESSIBLE:
        num_shareholders = int(str_num_shareholders)

    if num_shareholders > 0:
        name_list = raw_data['shareholder_full_names']
        num_shareholders = len(name_list) if name_list else 0

    shareholders_data = cast(ItemsView[str, list], {
        dest: raw_data.get(source, [''] * num_shareholders)
        for dest, source in SHAREHOLDER_FIELD_MAP.items()
    }.items())

    return [format_shareholder(shareholders_data, idx) for idx in range(num_shareholders)]
