import requests
from datetime import datetime
from schemad_types.utils import get_in
from requests.exceptions import RequestException, HTTPError
from functools import reduce

from app.utils import paginate, base_request, DueDilServiceException, convert_country_code,\
    send_exception, retry, BASE_API


def make_charity_url(country_code, charity_id, endpoint):
    return f'/charity/{country_code}/{charity_id}{endpoint}.json'


def request_paginated_attribute(url, attribute, credentials):
    status_code, json = base_request(url, credentials)

    if status_code != 200:
        return None, None

    values = json[attribute]
    pagination = json.get('pagination') or {}

    pages = paginate(url, pagination, credentials)
    values_pages = [json[attribute] for _, json in pages]
    values = reduce(lambda x, y: x + y, values_pages, values)

    return json, values


def request_vitals(country_code, charity_id, credentials):
    return base_request(make_charity_url(country_code, charity_id, ''), credentials)


def request_trustees(country_code, charity_id, credentials):
    url = make_charity_url(country_code, charity_id, '/trustees')
    return request_paginated_attribute(url, 'trustees', credentials)


def request_classifiers(country_code, charity_id, credentials):
    url = make_charity_url(country_code, charity_id, '/classifiers')
    return request_paginated_attribute(url, 'classifiers', credentials)


def request_areas_of_activity(country_code, charity_id, credentials):
    url = make_charity_url(country_code, charity_id, '/areas-of-activity')
    return request_paginated_attribute(url, 'areasOfActivity', credentials)


def find_charity_from_number(country_code, company_number, credentials):
    url = f'{BASE_API}/search/charities.json'
    query = {
        'criteria': {
            'name': company_number,
        }
    }
    headers = {'X-AUTH-TOKEN': credentials.get('auth_token')}

    response = retry(lambda: requests.post(url, json=query, headers=headers), (RequestException, HTTPError))

    charities = response.json()['charities']
    charities = [
        charity for charity in charities
        if get_in(charity, ['corporateIdentity', 'companyId']) == company_number
    ]

    if len(charities) > 0:
        return get_in(charities, [0, 'charityId'])

    return None


def format_trustee(trustee):
    name = trustee['sourceName']
    names = name.split(' ')
    return {
        'immediate_data': {
            'entity_type': 'INDIVIDUAL',
            'personal_details': {
                'name': {
                    'title': names[0],
                    'given_names': names[1:-1],
                    'family_name': names[-1],
                }
            }
        },
        'entity_type': 'INDIVIDUAL',
        'provider_name': 'DueDil'
    }


def get_charity(country_code, company_number, credentials):
    charity_id = find_charity_from_number(country_code, company_number, credentials)

    if charity_id is None:
        return None, None

    try:
        status_code, vitals = request_vitals(country_code, charity_id, credentials)
    except HTTPError:
        status_code = 500

    if status_code in [404, 500]:
        return None, None
    elif status_code != 200:
        raise DueDilServiceException(f'Request failed with status code {status_code}')

    corporate = vitals.get('corporateIdentity', {})

    country_of_incorporation_iso2 = corporate.get('countryCode')
    country_of_incorporation = convert_country_code(country_of_incorporation_iso2)

    registration_date = vitals.get('firstRegisteredDate')

    is_active = None
    if corporate.get('simplifiedStatus') is not None:
        is_active = corporate.get('simplifiedStatus') == 'Active'

    contact = vitals.get('officialContact', {})
    financial = vitals.get('financialSummary', {})
    currency = get_in(vitals, ['accounts', 'currency'])

    raw_areas, areas_of_activity = request_areas_of_activity(country_code, charity_id, credentials)
    raw_classifiers, classifiers = request_classifiers(country_code, charity_id, credentials)
    raw_trustees, trustees = request_trustees(country_code, charity_id, credentials)

    def get_classifiers(t):
        return [v.get('classifier') for v in classifiers if v.get('type') == t]

    return {
        'vitals': vitals,
        'areas_of_activity': raw_areas,
        'classifiers': raw_classifiers,
        'trustees': raw_trustees,
    }, {
        'metadata': {
            'name': vitals.get('name'),
            'number': corporate.get('companyId'),
            'charity_number': get_in(vitals, ['registeredAs', 'registeredCharityNumber']),
            'addresses': [
                {
                    'type': 'contact_address',
                    'address': {
                        'type': 'STRUCTURED',
                        'original_freeform_address': get_in(vitals, ['officialContact', 'address', 'fullAddress'])
                    }
                }
            ],
            'country_of_incorporation': country_of_incorporation,
            'number_of_employees': vitals.get('numberOfEmployees'),
            'is_active': is_active,
            'contact_details': {
                'email': contact.get('email'),
                'phone_number': contact.get('telephoneNumber'),
                'url': vitals.get('primaryWebsite'),
            },
            'areas_of_activity': [{'location': area.get('sourceName')} for area in areas_of_activity],
            'description': get_in(vitals, ['registeredAs', 'charitableObjects']),
        },
        'officers': {
            'trustees': [format_trustee(trustee) for trustee in trustees],
        },
        'charity_data': {
            'registration_date': registration_date,
            'number_of_volunteers': vitals.get('numberOfVolunteers'),
            'beneficiaries': get_classifiers('beneficiary'),
            'activity': get_classifiers('activity'),
            'purpose': get_classifiers('purpose'),
        },
        'financials': {
            'total_income_and_endowments': {
                'value': financial.get('totalIncomeAndEndowments'),
                'currency_code': currency,
            },
            'total_expenditure': {
                'value': financial.get('totalExpenditure'),
                'currency_code': currency,
            },
            'total_funds': {
                'value': financial.get('totalFunds'),
                'currency_code': currency,
            },
        }
    }
