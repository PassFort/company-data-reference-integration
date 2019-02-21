from typing import List, Any, Dict

import pycountry
import requests
from requests.exceptions import RequestException, HTTPError
from passfort_data_structure.entities.entity_type import EntityType

BASE_API = 'https://duedil.io/v4'


class DueDilAuthException(Exception):
    pass


class DueDilServiceException(Exception):
    pass

    def to_dict(self):
        return {'message': self.args[0]}


def tagged(val):
    return {'v': val}


def _get_pages(pagination):
    pagination = pagination or {}

    offset = pagination.get('limit', 1)
    limit = offset
    total = pagination.get('total', limit)

    if total < offset:
        return []

    while offset < total:
        yield (offset, limit)
        offset += limit


def paginate(url, pagination, credentials):
    pages = _get_pages(pagination)
    urls = [f'{url}?offset={offset}&limit={limit}' for offset, limit in pages]
    return [base_request(url, credentials, get) for url in urls]


# Makes multiple requests to the given paginated resources, combines the results, and gives back
# a response which appears as though a single request had been made with `limit == total`
def get_all_results(url, property, credentials) -> Dict[str, Any]:
    status_code, result = base_request(url, credentials, get)

    if status_code == 404:
        return {property: []}

    if status_code == 401 or status_code == 403:
        raise DueDilAuthException()

    if 400 <= status_code <= 499:
        raise DueDilServiceException(f'Received a {status_code} error from DueDil')

    if 500 <= status_code <= 599:
        raise DueDilServiceException(f'Internal error from DueDil: {status_code}')

    pagination = result['pagination']
    pages = paginate(url, pagination, credentials)

    pagination['limit'] = pagination['total']
    result[property] = [item for page in pages for item in page[property]]
    return result


def retry(f, excs, attempts=3):
    while True:
        try:
            return f()
        except excs:
            if attempts > 1:
                attempts -= 1
            else:
                raise


def get(url, credentials, json_data=None):
    response = requests.get(
        BASE_API + url,
        headers={'X-AUTH-TOKEN': credentials.get('auth_token')},
    )

    if 500 <= response.status_code < 600:
        raise HTTPError('Server Error', response)

    return response


def post(url, credentials, json_data):
    response = requests.post(
        BASE_API + url,
        headers={'X-AUTH-TOKEN': credentials.get('auth_token')},
        json=json_data
    )

    if 500 <= response.status_code < 600:
        raise HTTPError('Server Error', response)

    return response


def company_url(country_code, company_number, endpoint):
    return f'/company/{country_code}/{company_number}{endpoint}.json'


def charity_url(country_code, charity_id, endpoint):
    return f'/charity/{country_code}/{charity_id}{endpoint}.json'


def make_url(country_code, company_number, endpoint, offset=0, limit=10):
    return f'/company/{country_code}/{company_number}/{endpoint}.json?offset={offset}&limit={limit}'


def base_request(url, credentials, method=get, json_data=None):
    response = None
    json = None

    response = retry(lambda: method(url, credentials, json_data), (RequestException, HTTPError))
    json = response.json()

    if response.status_code != 200:
        return response.status_code, {}

    return response.status_code, json


def get_entity_type(duedil_type):
    if duedil_type == 'company':
        return EntityType.COMPANY
    else:
        return EntityType.INDIVIDUAL


def convert_country_code(country_code):
    if not country_code:
        return None
    return pycountry.countries.get(alpha_2=country_code).alpha_3


def send_exception(exception, custom_data=None):
    try:
        from app.application import sentry

        sentry.captureException(
            exc_info=(exception.__class__, exception, exception.__traceback__),
            extra=custom_data
        )
    except ImportError:
        pass


def string_compare(s1, s2):
    import string

    if (s1 is None) or (s2 is None):
        return False

    remove = string.punctuation + string.whitespace + '&'
    translation = str.maketrans('', '', remove)
    return s1.translate(translation).upper() == s2.translate(translation).upper()
