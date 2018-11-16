from schemad_types.utils import get_in
from uuid import uuid1
from functools import reduce

from passfort_data_structure.companies.ownership import Shareholder
from passfort_data_structure.entities.entity_type import EntityType

from app.utils import get, get_entity_type, DueDilServiceException, convert_country_code, make_url, \
    paginate, base_request, send_exception


def request_shareholders(country_code, company_number, credentials):
    """Fetches all shareholders for a given company.
    Args:
        - country_code: iso2 country code
        - company_number: string
        - credentials: object
    Returns:
        - raw_shareholders: object
        - shareholders: Shareholder[]

    Shareholder {
        first_names: string,
        last_name: string,
        resolver_id: uuid1,
        provider_name: duedil,
        shareholding: {
            share_class: string,
            amount: int,
            percentage: int,
            currency: "GBP"
        }
    }
    """

    url = f'/company/{country_code}/{company_number}/shareholders.json'

    status_code, json = base_request(url, credentials, get)

    if status_code >= 400 and status_code <= 499:
        raise(DueDilServiceException(f'Received a {status_code} error from DueDil'))

    if status_code != 200:
        return [], []

    shareholders = json['shareholders']
    pagination = json.get('pagination') or {}

    pages = paginate(url, pagination, credentials)
    shareholder_pages = [json['shareholders'] for _, json in pages]
    shareholders = reduce(lambda x, y: x + y, shareholder_pages, shareholders)

    return shareholders, format_shareholders(json['totalCompanyShares'], shareholders)


def format_fullname(entity_type, full_name):
    ''' Format names for storing purposes by concatenating them with underscores

    Args:
        entity_type: EntityType
        full_name: Stringg

    Returns:
        forenames: Forenames if a person
        surname: Surname if a person
    '''
    if entity_type == EntityType.COMPANY:
        return None, full_name

    names = full_name.split(' ')
    if len(names) == 1:
        return names[0], None
    else:
        return ' '.join(names[:-1]), names[-1]


def get_shareholder_entity_type(shareholder):
    not_matched = shareholder.get('notMatched')
    if not_matched is not None:
        return get_entity_type(not_matched.get('suspectedType'))

    possible_match = get_in(shareholder, ['possibleMatches', 0])
    if possible_match is not None:
        return get_entity_type(possible_match.get('type'))

    exact_match = get_in(shareholder, ['exactMatches', 0])
    if exact_match is not None:
        return get_entity_type(exact_match.get('type'))


def format_shareholders(total_shares, shareholders):
    '''
    Formats a DuedilShareholder into a Shareholder.
    Args:
        total_shares: int - the total shares of the company
        shareholders: list(DuedilShareholder)

    Returns:
        list(Shareholder)

    '''
    from functools import wraps

    def get_first_match_or_none(fn):
        @wraps(fn)
        def wrapped_fn(exact_matches):
            if exact_matches is None or exact_matches is []:
                return None
            # Only process it there is one match. Not clear how to merge multiple matches yet.
            if len(exact_matches) == 1:
                return fn(exact_matches[0])

            return None

        return wrapped_fn

    def format_shareholding(shareholding):
        number_of_shares = int(shareholding.get('numberOfShares'))
        return {
            'v': {
                'share_class': shareholding.get('class'),
                'amount': number_of_shares,
                'percentage': number_of_shares / total_shares,
                'currency': get_in(shareholding, ['nominalValue', 'currency']),
                'provider_name': 'DueDil'
            }
        }

    @get_first_match_or_none
    def format_dob(exact_match):
        from passfort_data_structure.misc.formatted_date import SchemadPartialDate

        year = get_in(exact_match, ['person', 'dateOfBirth', 'year'])
        month = get_in(exact_match, ['person', 'dateOfBirth', 'month'])
        day = get_in(exact_match, ['person', 'dateOfBirth', 'day'])
        if year or month or day:
            return SchemadPartialDate(year=year, month=month, day=day)

        return None

    @get_first_match_or_none
    def format_nationality(exact_match):
        nationalities = get_in(exact_match, ['person', 'nationalities'])

        if nationalities is None or nationalities is []:
            return None

        # Only return first nationality
        first_country_code = nationalities[0].get('countryCode')
        if first_country_code is not None and len(first_country_code) == 2:
            try:
                return convert_country_code(first_country_code)
            except KeyError:
                exc = DueDilServiceException('Unable to process country code')
                send_exception(exc, custom_data={
                    'country_code': first_country_code
                })

        return None

    @get_first_match_or_none
    def format_title(exact_match):
        return get_in(exact_match, ['person', 'honorific'])

    @get_first_match_or_none
    def format_company_country_of_incorporation(exact_match):
        country_code = get_in(exact_match, ['company', 'countryCode'])
        if country_code is not None and len(country_code) == 2:
            try:
                return convert_country_code(country_code)
            except KeyError:
                exc = DueDilServiceException('Unable to process country code')
                send_exception(exc, custom_data={
                    'country_code': country_code
                })
        return None

    @get_first_match_or_none
    def format_company_number(exact_match):
        return get_in(exact_match, ['company', 'companyId'])

    def format_shareholder(shareholder):
        entity_type = get_shareholder_entity_type(shareholder)
        first_names, surname = format_fullname(entity_type, shareholder.get('sourceName', ''))

        shareholder_matches = shareholder.get('exactMatches')
        return Shareholder({
            'title': format_title(shareholder_matches),
            'first_names': {'v': first_names},
            'last_name': {'v': surname},
            'dob': {'v': format_dob(shareholder_matches)},
            'nationality': {'v': format_nationality(shareholder_matches)},
            'company_number': format_company_number(shareholder_matches),
            'country_of_incorporation': format_company_country_of_incorporation(shareholder_matches),
            'resolver_id': uuid1(),
            'provider_name': 'DueDil',
            'type': {'v': entity_type},
            'shareholdings': list(map(format_shareholding, shareholder.get('shareholdings', [])))
        })

    return list(map(format_shareholder, shareholders))
