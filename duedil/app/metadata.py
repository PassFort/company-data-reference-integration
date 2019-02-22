import pycountry
from datetime import datetime
from schemad_types.utils import get_in
from passfort_data_structure.companies.metadata import CompanyMetadata, StructuredCompanyType, OwnershipType
from requests.exceptions import RequestException, HTTPError
from json import JSONDecodeError

from app.utils import get, make_url, base_request, DueDilServiceException, \
    convert_country_code, tagged, send_exception

STRUCTURED_COMPANY_TYPE_MAP = {
    'Private limited with share capital': StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Private company limited by shares': StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Anpartsselskab': StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Public limited with share capital': StructuredCompanyType({
        'is_public': tagged(True),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Limited Partnership': StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.PARTNERSHIP)
    }),
    'Private limited by guarantee without share capital':
    StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Private limited by guarantee without share capital, exempt from using "Limited"':
    StructuredCompanyType({
        'is_public': tagged(False),
        'is_limited': tagged(True),
        'ownership_type': tagged(OwnershipType.COMPANY)
    }),
    'Other': StructuredCompanyType({})
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


def structure_company_type(type_):
    try:
        return STRUCTURED_COMPANY_TYPE_MAP[type_]
    except (KeyError, ValueError):
        exc = CompanyTypeError(f'Unrecognised company type {type_}')
        send_exception(exc, custom_data={'company_type': type_})
        return StructuredCompanyType()


def request_phonenumbers(country_code, company_number, credentials):
    return base_request(
        make_url(country_code, company_number, 'telephone-numbers', limit=1),
        credentials,
        get
    )


def request_websites(country_code, company_number, credentials):
    return base_request(
        make_url(country_code, company_number, 'websites', limit=1),
        credentials,
        get
    )


def get_metadata(country_code, company_number, credentials):
    status_code, company_json = base_request(
        f'/company/{country_code}/{company_number}.json',
        credentials,
        get
    )

    if status_code == 404:
        return None, None

    address = get_in(company_json, ['registeredAddress', 'structuredAddress'], {})

    incorporation_date = company_json.get('incorporationDate')
    if incorporation_date:
        incorporation_date = datetime.strptime(incorporation_date, '%Y-%m-%d')

    address_country_iso2 = address.get('countryCode') or company_json.get('countryCode')
    address_country = convert_country_code(address_country_iso2)

    try:
        _, website_json = request_websites(country_code, company_number, credentials)
        website = get_in(website_json, ['websites', 0, 'website'])
    except (RequestException, HTTPError, JSONDecodeError):
        website = None

    try:
        _, telephone_json = request_phonenumbers(country_code, company_number, credentials)
        phone_number = get_in(telephone_json, ['telephoneNumbers', 0, 'telephoneNumber'])
    except (RequestException, HTTPError, JSONDecodeError):
        phone_number = None

    is_active = {'Active': True, 'Inactive': False}.get(company_json.get('simplifiedStatus'))

    return company_json, CompanyMetadata({
        'name': tagged(company_json.get('name')),
        'number': tagged(company_json.get('companyId')),
        'addresses': [
            {
                'type': 'registered_address',
                'address': {
                    'premise': address.get('premises'),
                    'route': address.get('thoroughfare'),
                    'locality': address.get('dependentLocality'),
                    'postal_town': address.get('postTown'),
                    'administrative_area_level_2': address.get('county'),
                    'postal_code': address.get('postcode'),
                    'country': address_country,

                    'latitude': get_in(company_json, ['registeredAddress', 'geolocation', 'latitude']),
                    'longitude': get_in(company_json, ['registeredAddress', 'geolocation', 'longitude']),

                    'original_address': get_in(company_json, ['registeredAddress', 'fullAddress']),
                }
            }
        ] if address_country else None,
        'country_of_incorporation': tagged(search_country_by_name(company_json.get('incorporationCountry'))),
        'is_active': tagged(is_active) if is_active is not None else None,
        'incorporation_date': tagged(incorporation_date),
        'company_type': tagged(company_json.get('type')),
        'structured_company_type': structure_company_type(company_json.get('type')),
        'contact_details': {
            'url': tagged(website),
            'phone_number': tagged(phone_number),
        } if phone_number or website else None,
    })
