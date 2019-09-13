import os
import requests
import nameparser

from app.utils import make_get, parse_int, parse_date


nameparser.config.CONSTANTS.suffix_acronyms.add('JP')
nameparser.config.CONSTANTS.suffix_acronyms.add('CC')
nameparser.config.CONSTANTS.suffix_acronyms.add('DL')
nameparser.config.CONSTANTS.suffix_acronyms.add('FRCR')
nameparser.config.CONSTANTS.suffix_acronyms.add('FRCP')
nameparser.config.CONSTANTS.suffix_acronyms.add('LLB')
nameparser.config.CONSTANTS.suffix_acronyms.add('FCA')
nameparser.config.CONSTANTS.suffix_acronyms.add('BA')
nameparser.config.CONSTANTS.suffix_acronyms.add('B.A.')
nameparser.config.CONSTANTS.suffix_acronyms.add('BSC')
nameparser.config.CONSTANTS.suffix_acronyms.add('BENG')
nameparser.config.CONSTANTS.suffix_acronyms.add('MENG')
nameparser.config.CONSTANTS.suffix_acronyms.add('MSC')
nameparser.config.CONSTANTS.suffix_acronyms.add('MA')
nameparser.config.CONSTANTS.suffix_acronyms.add('M.A.')
nameparser.config.CONSTANTS.suffix_acronyms.add('SSC')


ADDRESS_PARSER = os.environ.get('ADDRESS_PARSER_URL')


def format_description(getter):
    activities = getter('Activities')
    objects = getter('CharitableObjects')

    if activities and objects:
        return f'{activities}\n\n{objects}'
    elif activities:
        return activities
    else:
        return objects


ADDRESS_FIELDS = ['Line1', 'Line2', 'Line3', 'Line4', 'Line5', 'Postcode']
def format_address(address):
    freeform_address = ', '.join([address(f, strip=True) for f in ADDRESS_FIELDS if address(f, None)])
    try:
        return requests.post(ADDRESS_PARSER + '/parser', json={'query': freeform_address}).json()
    except:
        return {
            'type': 'STRUCTURED',
            "original_freeform_address": freeform_address,
        }


def format_trustee(trustee):
    name = nameparser.HumanName(trustee['TrusteeName'])
    return {
        'immediate_data': {
            'entity_type': 'INDIVIDUAL',
            'personal_details': {
                'name': {
                    'title': name.title,
                    'given_names': name.first.split() + name.middle.split(),
                    'family_name': name.last,
                }
            }
        },
        'entity_type': 'INDIVIDUAL',
        'provider_name': 'UK Charities Commission',
        'original_role': 'Trustee'
    }


def format_company_number(number):
    if number and len(number) < 8:
        return '0' * (8 - len(number)) + number
    return number


def format_financials(get):
    income_and_endowments = parse_int(get(['Returns', -1, 'Resources', 'Incoming', 'Total'], None))
    expenditure = parse_int(get(['Returns', -1, 'Resources', 'Expended', 'Total'], None))
    funds = parse_int(get(['Returns', -1, 'AssetsAndLiabilities', 'Funds', 'TotalFunds'], None))

    return {
        'total_income_and_endowments': {
            'value': income_and_endowments,
            'currency_code': 'GBP',
        } if income_and_endowments else None,
        'total_expenditure': {
            'value': expenditure,
            'currency_code': 'GBP',
        } if expenditure else None,
        'total_funds': {
            'value': funds,
            'currency_code': 'GBP',
        } if funds else None,
    }


def format_charity(data):
    get = make_get(data)

    company_number = format_company_number(get('RegisteredCompanyNumber', None, strip=True))
    address_get = make_get(get('Address')) if get('Address', None) else None
    registration_date = parse_date(get(['RegistrationHistory', 0, 'RegistrationDate'], None))

    is_active = None
    if get('OrganisationType') == 'R':
        is_active = True
    elif get('OrganisationType') == 'RM':
        is_active = False


    return {
        'metadata': {
            'name': get('CharityName', strip=True),
            'number': company_number,
            'uk_charity_commission_number': str(get('RegisteredCharityNumber')),
            'addresses': [format_address(address_get)] if address_get else [],
            'country_of_incorporation': 'GBR' if company_number else None,
            'number_of_employees': parse_int(get(['Returns', -1, 'Employees', 'NoEmployees'], None)),
            'is_active': is_active,
            'contact_details': {
                'email': get('EmailAddress', None, strip=True),
                'phone_number': get('PublicTelephoneNumber', None, strip=True),
                'url': get('WebsiteAddress', None, strip=True),
            },
            'areas_of_activity': [{'location': area.strip()} for area in get('AreaOfOperation', [])],
            'description': format_description(get),
        },
        'officers': {
            'trustees': [format_trustee(trustee) for trustee in data['Trustees']],
        },
        'charity_data': {
            'registration_date': registration_date,
            'number_of_volunteers': parse_int(get(['Returns', -1, 'Employees', 'NoVolunteers'], None)),
            'beneficiaries': [b.strip() for b in get(['Classification', 'Who'], [])],
            'activity': [c.strip() for c in get(['Classification', 'How'], [])],
            'purpose': [p.strip() for p in get(['Classification', 'What'], [])],
        },
        'financials': format_financials(get)
    }
