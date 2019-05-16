from datetime import datetime
from schemad_types.utils import get_in
from functools import reduce

from passfort_data_structure.companies.officers import Officer
from passfort_data_structure.entities.entity_type import EntityType

from app.utils import paginate, base_request, get, DueDilAuthException, DueDilServiceException, get_all_results, \
    company_url


def provider_role_to_key_mapping(officialRole):
    return {
        'director': 'directors',
        'secretary': 'secretaries',
        'llp_member': 'partners',
        'llp_designated_member': 'partners'
    }.get(officialRole.lower(), 'other')


def request_officers(country_code, company_number, credentials):
    """
    Args:
        - country_code: iso2 country code
        - company_number: string
        - credentials: object
    Returns:
        - raw_officers: object
        - officers: Officers[]

    Pagination object:
    ```
        "pagination": {
          "offset": 0,
          "limit": 10,
          "total": 12
        }
    ```
    """
    json = get_all_results(company_url(country_code, company_number, '/officers'), 'officers', credentials)

    officers = json['officers']

    return officers, format_officers(officers)


def format_officer_data(elem):
    officer = None
    if elem['type'] == "person":
        first_name = get_in(elem, ['person', 'firstName'], default='').split(' ')
        middle_name = get_in(elem, ['person', 'middleName'], default='').split(' ')

        first_names = []
        first_names.extend(first_name)
        first_names.extend(middle_name)
        first_names = filter(bool, first_names)

        officer = {
            "first_names": {"v": " ".join(first_names)},
            "last_name": {"v": get_in(elem, ['person', 'lastName'], '')},
            "type": {"v": EntityType.INDIVIDUAL},
        }

        dobMonth = get_in(elem, ['person', 'dateOfBirth', 'month'])
        dobYear = get_in(elem, ['person', 'dateOfBirth', 'year'])
        if dobMonth and dobYear:
            dob = datetime.strptime("{}-{}".format(dobYear, dobMonth), "%Y-%m")
            officer['dob'] = {"v": dob}
        elif dobYear:
            dob = datetime.strptime("{}".format(dobYear), "%Y")
            officer['dob'] = {"v": dob}

    elif elem['type'] == "company":
        officer = {
            "last_name": {"v": get_in(elem, ['company', 'name'])},
            "type": {"v": EntityType.COMPANY},
        }

    return officer


def format_officers(officers):
    def add_officer_roles_to_result(result, elem):

        officer_data = format_officer_data(elem)

        if officer_data:
            appointments = elem.get('appointments') or []

            for appt in appointments:
                # Required fields
                officer_with_role = Officer(officer_data)
                officer_with_role.original_role = {'v': appt['officialRole']}
                officer_with_role.provider_name = 'Duedil'

                start_date = appt['startDate']
                if start_date:
                    officer_with_role.appointed_on = {
                        'v': datetime.strptime(start_date, "%Y-%m-%d")
                    }
                end_date = appt['endDate']
                if end_date:
                    officer_with_role.resigned_on = {
                        'v': datetime.strptime(end_date, "%Y-%m-%d")
                    }

                passfort_role_key = provider_role_to_key_mapping(
                    officer_with_role.original_role.v
                ) if appt['officialRole'] else 'other'

                result[passfort_role_key].append(officer_with_role)

                if officer_with_role.resigned_on and officer_with_role.resigned_on.v < datetime.now():
                    result['resigned'].append(officer_with_role)

        return result

    result_by_role = {
        'directors': [],
        'secretaries': [],
        'partners': [],
        'resigned': [],
        'other': []
    }

    return reduce(add_officer_roles_to_result, officers, result_by_role) if officers is not None else None
