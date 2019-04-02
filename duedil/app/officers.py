from datetime import datetime
from schemad_types.utils import get_in
from functools import reduce

from passfort_data_structure.companies.officers import Officer
from passfort_data_structure.entities.entity_type import EntityType
from passfort_data_structure.entities.role import Role

from app.utils import paginate, base_request, get, DueDilAuthException, DueDilServiceException, get_all_results, \
    company_url


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


def format_officers(officers):
    def format_officer(elem):
        officer = None

        if elem['type'] == "person":
            first_name = get_in(elem, ['person', 'firstName'], default='').split(' ')
            middle_name = get_in(elem, ['person', 'middleName'], default='').split(' ')

            first_names = []
            first_names.extend(first_name)
            first_names.extend(middle_name)
            first_names = filter(bool, first_names)

            officer = Officer({
                "first_names": {"v": " ".join(first_names)},
                "last_name": {"v": get_in(elem, ['person', 'lastName'], '')},
                "type": {"v": EntityType.INDIVIDUAL},
            })

            dobMonth = get_in(elem, ['person', 'dateOfBirth', 'month'])
            dobYear = get_in(elem, ['person', 'dateOfBirth', 'year'])
            if dobMonth and dobYear:
                dob = datetime.strptime("{}-{}".format(dobYear, dobMonth), "%Y-%m")
                officer.dob = {"v": dob}
            elif dobYear:
                dob = datetime.strptime("{}".format(dobYear), "%Y")
                officer.dob = {"v": dob}

        elif elem['type'] == "company":
            officer = Officer({
                "last_name": {"v": get_in(elem, ['company', 'name'])},
                "type": {"v": EntityType.COMPANY},
            })

        if officer:
            officer.provider_name = 'DueDil'

            official_role = get_in(elem, ['appointments', 0, 'officialRole'])
            if official_role:
                officer.original_role = {'v': official_role}

            start_date = get_in(elem, ['appointments', 0, 'startDate'])
            if start_date:
                officer.appointed_on = {
                    "v": datetime.strptime(start_date, "%Y-%m-%d")}
            end_date = get_in(elem, ['appointments', 0, 'endDate'])
            if end_date:
                officer.resigned_on = {
                    "v": datetime.strptime(end_date, "%Y-%m-%d")}

        return officer

    return [format_officer(entry) for entry in officers] if officers is not None else None
