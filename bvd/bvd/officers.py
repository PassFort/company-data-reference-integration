from typing import Dict, List, Optional, ItemsView, Tuple, cast
from enum import Enum
from datetime import datetime

from pycountry import countries

from bvd.utils import CompanyRawData
from bvd.format_utils import BaseObject, EntityType, format_names, format_date

DATA_NOT_ACCESSIBLE = 'Data is not accessible'
OFFICER_FIELD_MAP = {
    'full_name': 'officer_full_names',
    'first_name': 'officer_first_names',
    'middle_names': 'officer_middle_names',
    'last_name': 'officer_last_names',
    'type': 'officer_types',
    'role': 'officer_roles',
    'appointed_on': 'officer_appointed_dates',
    'resigned_on': 'officer_resigned_dates',
    'nationalities': 'officer_nationalities',
    'dob': 'officer_dobs',
    'uci': 'officer_ucis',
    'bvd_id': 'officer_bvd_ids',
    'current_previous': 'officer_current_previous',
}

OFFICER_TYPE_MAP = {
    'Individual': EntityType.INDIVIDUAL,
    'Company': EntityType.COMPANY,
}

OfficerRawData = Dict[str, str]


class OfficerRole(Enum):
    INDIVIDUAL_DIRECTOR = 'INDIVIDUAL_DIRECTOR'
    INDIVIDUAL_COMPANY_SECRETARY = 'INDIVIDUAL_COMPANY_SECRETARY'
    INDIVIDUAL_OTHER = 'INDIVIDUAL_OTHER'
    COMPANY_DIRECTOR = 'COMPANY_DIRECTOR'
    COMPANY_COMPANY_SECRETARY = 'COMPANY_COMPANY_SECRETARY'
    COMPANY_OTHER = 'COMPANY_OTHER'


def format_officer_role(type_: EntityType, original_role: str) -> OfficerRole:
    original_role_lower = original_role.lower()
    if 'director' in original_role_lower:
        return OfficerRole.INDIVIDUAL_DIRECTOR if type_ is EntityType.INDIVIDUAL else OfficerRole.COMPANY_DIRECTOR
    if 'secretary' in original_role_lower:
        return OfficerRole.INDIVIDUAL_COMPANY_SECRETARY if type_ is EntityType.INDIVIDUAL \
            else OfficerRole.COMPANY_COMPANY_SECRETARY
    else:
        return OfficerRole.INDIVIDUAL_OTHER if type_ is EntityType.INDIVIDUAL else OfficerRole.COMPANY_OTHER


def format_officer_names(type_: EntityType, raw_data: OfficerRawData) -> Tuple[str, str]:
    first_name = raw_data['first_name']
    middle_name = raw_data['middle_names']
    first_names = ' '.join([first_name, middle_name]) if middle_name else first_name

    return format_names(
        first_names,
        raw_data['last_name'],
        raw_data['full_name'],
        type_,
    )


def format_nationality(country_name: str) -> Optional[str]:
    try:
        return countries.get(name=country_name).alpha_3
    except AttributeError:
        return None


def format_nationalities(raw_data: OfficerRawData) -> List[str]:
    raw_nationalities = raw_data.get('nationalities')
    if raw_nationalities:
        codes = [format_nationality(name) for name in raw_nationalities.split(';')]
        return [code for code in codes if code is not None]

    return []


class Officer(BaseObject):
    bvd_id: str
    bvd_uci: str
    type: EntityType
    role: OfficerRole
    original_role: str
    first_names: str
    last_name: str
    nationality: str
    resigned: bool
    appointed_on: Optional[datetime]
    resigned_on: Optional[datetime]
    dob: Optional[datetime]

    @staticmethod
    def from_raw_data(raw_data: OfficerRawData) -> 'Officer':
        officer = Officer()
        officer.bvd_id = raw_data['bvd_id']
        officer.bvd_uci = raw_data['uci']
        officer.type = OFFICER_TYPE_MAP[raw_data['type']]
        officer.role = format_officer_role(officer.type, raw_data['role'])
        officer.original_role = raw_data['role']
        first_names, last_name = format_officer_names(officer.type, raw_data)
        officer.first_names = first_names
        officer.last_name = last_name
        nationalities = format_nationalities(raw_data)
        if len(nationalities) > 0:
            officer.nationality = nationalities[0]

        officer.resigned = raw_data['current_previous'] == 'Previous'
        officer.appointed_on = format_date(raw_data['appointed_on'])
        officer.resigned_on = format_date(raw_data['resigned_on'])
        officer.dob = format_date(raw_data['dob'])
        return officer


class Officers(BaseObject):
    directors: List[Officer]
    secretaries: List[Officer]
    resigned: List[Officer]
    others: List[Officer]

    def __init__(self):
        self.directors = []
        self.secretaries = []
        self.resigned = []
        self.others = []


def format_officer(officers_data: ItemsView[str, list], idx: int) -> Officer:
    officer_data: OfficerRawData = {attr: value[idx] for attr, value in officers_data}
    return Officer.from_raw_data(officer_data)


def _format_officers(raw_data: CompanyRawData) -> List[Officer]:
    str_num_officers: Optional[str] = raw_data.get('num_officers')
    num_officers = 0
    if str_num_officers and str_num_officers != DATA_NOT_ACCESSIBLE:
        num_officers = int(str_num_officers)

    officer_full_names = raw_data.get('officer_full_names')
    if num_officers > 0 and officer_full_names:
        num_officers = len(officer_full_names)

    officers_data = cast(ItemsView[str, list], {
        dest: raw_data.get(source, [''] * num_officers)
        for dest, source in OFFICER_FIELD_MAP.items()
    }.items())

    return [format_officer(officers_data, idx) for idx in range(num_officers)]


def format_officers(raw_data: CompanyRawData) -> Officers:
    officers = Officers()
    for officer in _format_officers(raw_data):
        if officer.resigned:
            officers.resigned.append(officer)
        elif officer.role in (OfficerRole.INDIVIDUAL_DIRECTOR, OfficerRole.COMPANY_DIRECTOR):
            officers.directors.append(officer)
        elif officer.role in (OfficerRole.INDIVIDUAL_COMPANY_SECRETARY, OfficerRole.COMPANY_COMPANY_SECRETARY):
            officers.secretaries.append(officer)
        else:
            officers.others.append(officer)

    return officers
