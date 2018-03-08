import pycountry
import requests
from requests.exceptions import RequestException, HTTPError
from passfort_data_structure.entities.entity_type import EntityType

BASE_API = 'https://duedil.io/v4'


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


def make_url(country_code, company_number, endpoint, offset=0, limit=10):
    return f'/company/{country_code}/{company_number}/{endpoint}.json?offset={offset}&limit={limit}'


def base_request(url, credentials, method, json_data=None):
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
    from app.application import sentry

    if sentry:
        sentry.captureException(
            exc_info=(exception.__class__, exception, exception.__traceback__),
            extra=custom_data
        )
