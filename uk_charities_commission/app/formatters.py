import os
import requests
import nameparser

from app.utils import parse_int, parse_date


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


def format_description(charities):
    activities = charities.Activities
    objects = charities.CharitableObjects

    if activities and objects:
        return f'{activities}\n\n{objects}'
    elif activities:
        return activities
    else:
        return objects


def format_address(address):
    freeform_address = ''
    if address.Line1:
        freeform_address += address.Line1.strip()
    if address.Line2:
        freeform_address += f', {address.Line2.strip()}'
    if address.Line3:
        freeform_address += f', {address.Line3.strip()}'
    if address.Line4:
        freeform_address += f', {address.Line4.strip()}'
    if address.Line5:
        freeform_address += f', {address.Line5.strip()}'
    if address.Postcode:
        freeform_address += f', {address.Postcode.strip()}'

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


def format_financials(return_):
    resources = return_.Resources if return_ else None
    assets_and_liabilities = return_.AssetsAndLiabilities if return_ else None
    income_and_endowments = parse_int(resources.Incoming.Total) if resources and resources.Incoming else None
    expenditure = parse_int(resources.Expended.Total) if resources and resources.Expended else None
    funds = parse_int(assets_and_liabilities.Funds.TotalFunds) if assets_and_liabilities and assets_and_liabilities.Funds else None

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


def strip(string):
    if string is not None:
        return string.strip()


def format_charity(charity):
    company_number = format_company_number(strip(charity.RegisteredCompanyNumber))
    registration_date = parse_date(charity.RegistrationHistory[0].RegistrationDate) if len(charity.RegistrationHistory) > 0 else None

    is_active = None
    if charity.OrganisationType == 'R':
        is_active = True
    elif charity.OrganisationType == 'RM':
        is_active = False

    latest_return = charity.Returns[-1] if len(charity.Returns) > 0 else None

    return {
        'metadata': {
            'name': strip(charity.CharityName),
            'number': company_number,
            'uk_charity_commission_number': str(charity.RegisteredCharityNumber),
            'addresses': [format_address(charity.Address)] if charity.Address else [],
            'country_of_incorporation': 'GBR' if company_number else None,
            'number_of_employees': parse_int(latest_return.Employees.NoEmployees) if latest_return and latest_return.Employees else None,
            'is_active': is_active,
            'contact_details': {
                'email': strip(charity.EmailAddress),
                'phone_number': strip(charity.PublicTelephoneNumber),
                'url': strip(charity.WebsiteAddress),
            },
            'areas_of_activity': [{'location': strip(area)} for area in charity.AreaOfOperation or []],
            'description': format_description(charity),
        },
        'officers': {
            'trustees': [format_trustee(trustee) for trustee in charity.Trustees or []],
        },
        'charity_data': {
            'registration_date': registration_date,
            'number_of_volunteers': parse_int(latest_return.Employees.NoVolunteers) if latest_return and latest_return.Employees else None,
            'beneficiaries': [strip(b) for b in charity.Classification.Who or []] if charity.Classification else None,
            'activity': [c.strip() for c in charity.Classification.How or []] if charity.Classification else None,
            'purpose': [p.strip() for p in charity.Classification.What or []] if charity.Classification else None,
        },
        'financials': format_financials(latest_return) if latest_return else None
    }
