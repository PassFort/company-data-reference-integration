from datetime import datetime

from requests.exceptions import RequestException, HTTPError
from json import JSONDecodeError

from app.utils import get_all_results, company_url


def request_fca_authorisations(country_code, company_number, credentials):
    return get_all_results(
        company_url(country_code, company_number, '/fca-authorisations'),
        'fcaAuthorisations',
        credentials
    )['fcaAuthorisations']


def get_authorisations(country_code, company_number, credentials):
    try:
        raw_fca_authorisations = request_fca_authorisations(country_code, company_number, credentials)
    except (RequestException, HTTPError, JSONDecodeError):
        raw_fca_authorisations = None

    return raw_fca_authorisations, [{
        'authority': 'FCA',
        'source_name': auth['sourceName'],
        'firm_type': auth['firmType'],
        'reference_number': auth['referenceNumber'],
        'status': auth['status'],
        'status_description': auth['statusDescription'],
        'effective_date': datetime.strptime(auth['effectiveDate'], '%Y-%m-%d'),
        'permissions': [{
            'activity_category': perm['activityCategory'],
            'activity_description': perm['activityDescription'],
        } for perm in auth['permissions']],
        'updated_from_source': datetime.strptime(auth['updatedFromSource'], '%Y-%m-%d'),
    } for auth in raw_fca_authorisations] if raw_fca_authorisations is not None else None
