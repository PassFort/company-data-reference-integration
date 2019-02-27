from schemad_types.utils import get_in
from uuid import uuid1
from functools import wraps

from passfort_data_structure.companies.ownership import Shareholder
from passfort_data_structure.entities.entity_type import EntityType

from app.utils import DueDilServiceException, convert_country_code, send_exception, get_all_results, company_url


HONORIFICS = {'mr', 'mrs', 'miss', 'ms', 'mx', 'master', 'sir', 'madam', 'mdm', 'lord', 'lady', 'sire', 'dame', 'dr',
              'prof', 'professor'}


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

    json = get_all_results(company_url(country_code, company_number, '/shareholders'), 'shareholders', credentials)

    shareholders = json['shareholders']
    if shareholders is None:
        return [], []

    total_company_shares = json['totalCompanyShares']

    return shareholders, format_shareholders(total_company_shares, shareholders)


def request_pscs(country_code, company_number, credentials):
    """Fetches all pscs for a given company.
    Args:
        - country_code: iso2 country code
        - company_number: string
        - credentials: object
    Returns:
        - raw_pscs: object
        - pscs: Shareholder[]

    Shareholder {
        first_names: string,
        last_name: string,
        resolver_id: uuid1,
        provider_name: duedil,
    }
    """

    json = get_all_results(
        company_url(country_code, company_number, '/persons-significant-control'),
        'personsOfSignificantControl',
        credentials
    )

    pscs = json['personsOfSignificantControl']
    statements = json['statements']

    return pscs, format_pscs(statements, pscs)


def format_fullname(full_name):
    ''' Format names for storing purposes by concatenating them with underscores

    Args:
        full_name: String

    Returns:
        title: Title
        forenames: Forenames
        surname: Surname
    '''
    title = None
    names = full_name.split(' ')
    if len(names) == 1:
        return title, names[0], None
    elif len(names) > 1:
        potential_title = names[0].strip(' -.\',').lower()
        if potential_title in HONORIFICS:
            title = names[0]
            names = names[1:]

        return title, ' '.join(names[:-1]), names[-1]
    else:
        return None, None, None


def tag(v):
    return {'v': v} if v is not None else None


def find_best_matches(obj, known_match):
    exact_matches = get_in(obj, ['exactMatches']) or []
    possible_matches = get_in(obj, ['possibleMatches']) or []
    ordered_matches = list(filter(None, exact_matches + [known_match] + possible_matches))

    suspected_type = get_in(obj, ['notMatched', 'suspectedType'])
    if suspected_type:
        ordered_matches.append({suspected_type: {'present': True}})

    matches_with_type = [match for match in ordered_matches if match.get('person') or match.get('company')]

    if len(matches_with_type) == 0:
        return None, None

    if matches_with_type[0].get('person'):
        actual_type = 'person'
    else:
        actual_type = 'company'

    filtered_matches = [
        match.get(actual_type) or match.get('unknown')
        for match in ordered_matches
        if match.get(actual_type) or match.get('unknown')
    ]

    # Avoid mixing more than one other data source with the known match
    return actual_type, filtered_matches[:2]


def get_first_match_or_none(fn):
    @wraps(fn)
    def wrapped_fn(ordered_matches):
        for match in ordered_matches:
            result = fn(match)
            if result is not None:
                return result
        return None

    return wrapped_fn


def build_individual_shareholder(matches):
    @get_first_match_or_none
    def individual_get_names(match):
        if match.get('firstName') or match.get('lastName'):
            first_names = (match.get('firstName') or '').split(' ')
            middle_names = (match.get('middleName') or '').split(' ')
            given_names = [name for name in first_names + middle_names if name]
            return match.get('honorific'), ' '.join(given_names), match.get('lastName')
        elif match.get('sourceName'):
            return format_fullname(match['sourceName'])
        else:
            return None

    @get_first_match_or_none
    def individual_get_dob(match):
        from passfort_data_structure.misc.formatted_date import SchemadPartialDate

        year = get_in(match, ['dateOfBirth', 'year'])
        month = get_in(match, ['dateOfBirth', 'month'])
        day = get_in(match, ['dateOfBirth', 'day'])
        if year or month or day:
            return SchemadPartialDate(year=year, month=month, day=day)

        return None

    @get_first_match_or_none
    def individual_get_nationality(match):
        nationalities = match.get('nationalities')
        if not nationalities:
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

    names = individual_get_names(matches)
    if names:
        title, first_names, last_name = names
    else:
        title, first_names, last_name = None, None, None

    return Shareholder(
        title=title,
        first_names=tag(first_names),
        last_name=tag(last_name),
        dob=tag(individual_get_dob(matches)),
        nationality=tag(individual_get_nationality(matches)),
        type=tag(EntityType.INDIVIDUAL)
    )


def build_company_shareholder(matches):
    @get_first_match_or_none
    def company_get_name(match):
        return match.get('sourceName') or match.get('name')

    @get_first_match_or_none
    def company_get_country_of_incorporation(match):
        country_code = match.get('countryCode')
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
    def company_get_number(match):
        return match.get('companyId') or match.get('registrationNumber')

    return Shareholder(
        last_name=tag(company_get_name(matches)),
        country_of_incorporation=company_get_country_of_incorporation(matches),
        company_number=company_get_number(matches),
        type=tag(EntityType.COMPANY)
    )


def build_shareholder(total_shares, obj):
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

    type, matches = find_best_matches(obj, {'unknown': obj})
    if type is None:
        return None

    if type == 'person':
        shareholder = build_individual_shareholder(matches)
    else:
        shareholder = build_company_shareholder(matches)

    shareholder.resolver_id = uuid1()
    shareholder.provider_name = 'DueDil'
    shareholder.shareholdings = list(map(format_shareholding, obj.get('shareholdings', [])))
    return shareholder


def format_shareholders(total_shares, objs):
    result = [build_shareholder(total_shares, obj) for obj in objs]
    return list(filter(None, result))


def build_psc(obj):
    type, matches = find_best_matches(obj, obj)
    if type is None:
        return None

    if type == 'person':
        shareholder = build_individual_shareholder(matches)
    else:
        shareholder = build_company_shareholder(matches)

    shareholder.resolver_id = uuid1()
    shareholder.provider_name = 'DueDil'
    return shareholder


def format_pscs(_statements, objs):
    result = [build_psc(obj) for obj in objs]
    return list(filter(None, result))

