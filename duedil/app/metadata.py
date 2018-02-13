import pycountry
from datetime import datetime
from schemad_types.utils import get_in
from passfort_data_structure.companies.metadata import CompanyMetadata
from requests.exceptions import RequestException, HTTPError
from json import JSONDecodeError

from app.utils import paginate, make_url, base_request, DueDilServiceException,\
    convert_country_code, tagged, send_exception

COMPANY_TYPES = {
    'Private limited with share capital': 'ltd',
    'Other': 'unknown',
    '': 'unknown',
    None: 'unknown',
}


class CompanyTypeError(DueDilServiceException):
    pass


def search_country_by_name(q):
    if q is None:
        return

    lq = q.lower()

    for country in pycountry.countries:
        if lq == country.name.lower():
            return country.alpha_3


def get_company_type(type_):
    try:
        COMPANY_TYPES[type_]
    except KeyError:
        exc = CompanyTypeError(f'Unable to process company type {type_}')
        send_exception(exc, custom_data={'company_type': type_})
        raise exc


def request_phonenumbers(country_code, company_number, credentials):
    return base_request(
        make_url(country_code, company_number, 'telephone-numbers', limit=1),
        credentials,
    )


def request_websites(country_code, company_number, credentials):
    return base_request(
        make_url(country_code, company_number, 'websites', limit=1),
        credentials,
    )


def get_metadata(country_code, company_number, credentials):
    status_code, json = base_request(
        f'/company/{country_code}/{company_number}.json',
        credentials,
    )

    if status_code == 404:
        return None, None

    address = get_in(json, ['registeredAddress', 'structuredAddress'], {})

    incorporation_date = json.get('incorporationDate')
    if incorporation_date:
        incorporation_date = datetime.strptime(incorporation_date, '%Y-%m-%d')

    address_country_iso2 = address.get('countryCode') or json.get('countryCode')
    address_country = convert_country_code(address_country_iso2)

    try:
        _, json = request_websites(country_code, company_number, credentials)
        website = get_in(json, ['websites', 0, 'website'])
    except (RequestException, HTTPError, JSONDecodeError):
        website = None

    try:
        _, json = request_phonenumbers(country_code, company_number, credentials)
        phone_number = get_in(json, ['telephoneNumbers', 0, 'telephoneNumber'])
    except (RequestException, HTTPError, JSONDecodeError):
        phone_number = None

    return json, CompanyMetadata({
        'name': tagged(json.get('name')),
        'number': tagged(json.get('companyId')),
        'addresses': [
            {
                'type': 'STRUCTURE',
                'address': {
                    'premise': address.get('premises'),
                    'route': address.get('thoroughfare'),
                    'locality': address.get('dependentLocality'),
                    'postal_town': address.get('postTown'),
                    'administrative_area_level_2': address.get('county'),
                    'postal_code': address.get('postcode'),
                    'country': address_country,

                    'latitude': get_in(json, ['registeredAddress', 'geolocation', 'latitude']),
                    'longitude': get_in(json, ['registeredAddress', 'geolocation', 'longitude']),

                    'original_address': get_in(json, ['registeredAddress', 'fullAddress']),
                }
            }
        ] if address_country else None,
        'country_of_incorporation': tagged(search_country_by_name(json.get('incorporationCountry'))),
        'is_active': tagged(json.get('simplifiedStatus') == 'Active'),
        'incorporation_date': tagged(incorporation_date),
        'company_type': tagged(get_company_type(json.get('type'))),
        'contact_details': {
            'url': tagged(website),
            'phone_number': tagged(phone_number),
        } if phone_number or website else None
    })
