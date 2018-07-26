import requests
from datetime import datetime
from schemad_types.utils import get_in
from requests.exceptions import RequestException, HTTPError
from functools import reduce

from app.utils import paginate, base_request, DueDilServiceException, convert_country_code,\
    send_exception, retry, BASE_API, string_compare


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


def perform_search(country_code, search_term, credentials):
    url = f'{BASE_API}/search/charities.json'
    query = {'criteria': {'name': search_term}}
    headers = {'X-AUTH-TOKEN': credentials.get('auth_token')}

    response = retry(lambda: requests.post(url, json=query, headers=headers), (RequestException, HTTPError))
    return response.json()['charities']


def find_charity_candidates(country_code, company_number, name, credentials):
    charities = perform_search(country_code, company_number, credentials)

    if len(charities) == 0:
        charities = perform_search(country_code, name, credentials)

    return charities


def find_charity(country_code, company_number, name, credentials):
    candidates = find_charity_candidates(country_code, company_number, name, credentials)

    def is_match(charity):
        return get_in(charity, ['corporateIdentity', 'companyId']) == company_number or \
            string_compare(get_in(charity, ['name']), name) or \
            string_compare(get_in(charity, ['corporateIdentity', 'name']), name)

    def is_registered(charity):
        return get_in(charity, ['currentStatus', 'status']) == 'REGISTERED'

    candidates = [charity for charity in candidates if is_match(charity)]

    if len(candidates) == 0:
        return None

    if len(candidates) == 1:
        return get_in(candidates, [0, 'charityId'])

    # Still multiple candidates, let's try and return the first active candidate, if there are any

    active_candidates = [charity for charity in candidates if is_registered(charity)]
    if len(active_candidates) > 0:
        return get_in(active_candidates, [0, 'charityId'])

    # Giveup and just return first candidate

    return get_in(candidates, [0, 'charityId'])


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


def get_charity(country_code, company_number, name, credentials):
    charity_id = find_charity(country_code, company_number, name, credentials)

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

    corporate = vitals.get('corporateIdentity', {}) or {}

    country_of_incorporation_iso2 = corporate.get('countryCode')
    country_of_incorporation = convert_country_code(country_of_incorporation_iso2)

    registration_date = vitals.get('firstRegisteredDate')

    is_active = None
    if corporate.get('simplifiedStatus') is not None:
        is_active = corporate.get('simplifiedStatus') == 'Active'

    contact = vitals.get('officialContact', {})
    financials = vitals.get('financialSummary')
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
            'uk_charity_commission_number': get_in(vitals, ['registeredAs', 'registeredCharityNumber']),
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
                'value': financials.get('totalIncomeAndEndowments'),
                'currency_code': currency,
            },
            'total_expenditure': {
                'value': financials.get('totalExpenditure'),
                'currency_code': currency,
            },
            'total_funds': {
                'value': financials.get('totalFunds'),
                'currency_code': currency,
            },
        } if currency and financials else None
    }
