import json

from typing import List, Dict, Optional, Union, Tuple, Callable, Any, IO, cast
from requests import post
from requests.exceptions import RequestException, HTTPError
from requests.models import Response
from json import JSONDecodeError
from os import listdir
from os.path import dirname, abspath, join, splitext
from datetime import datetime

from bvd.format_utils import BaseObject


class BvDServiceException(Exception):
    status_code: int

    def __init__(self, status_code: int, message: str) -> None:
        self.status_code = status_code
        self.message = message


class BvDAuthException(BvDServiceException):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


CompanyRawData = Dict[str, Optional[Any]]
MatchCriteria = Dict[str, str]
BvDConfig = Dict[str, str]


class BvDInvalidConfigException(BvDServiceException):
    pass


class BvDEmptyResponseException(Exception):
    pass


REQUEST_EXCEPTIONS = (RequestException, JSONDecodeError, HTTPError)

BvDErrorConnectionError = 302
BvDErrorUnknownError = 303


class BvDError(BaseObject):
    source: str
    code: int
    message: str
    info: dict

    def __init__(self, e):
        self.source = 'PROVIDER'
        if isinstance(e, REQUEST_EXCEPTIONS)\
           or isinstance(e, BvDInvalidConfigException)\
           or isinstance(e, BvDAuthException):
            self.code = BvDErrorConnectionError
        else:
            self.code = BvDErrorUnknownError

        if hasattr(e, 'message'):
            self.message = e.message
        else:
            self.message = str(e)

        self.info = {
            "provider": "BvD",
            "timestamp": str(datetime.now()),
            "original_error": str(e),
        }


def send_sentry_exception(exception, custom_data=None):
    try:
        from app.application import sentry

        sentry.captureException(
            exc_info=(exception.__class__, exception, exception.__traceback__),
            extra=custom_data
        )
    except ImportError:
        pass


def make_default_exception(status_code: int) -> BvDServiceException:
    return BvDServiceException(status_code, 'Something went wrong')


def make_response_exception(response: Response) -> BvDServiceException:
    response_body = response.json()
    if type(response_body) is dict and response_body.get('ExceptionMessage'):
        return BvDServiceException(response.status_code, response_body['ExceptionMessage'])

    return make_default_exception(response.status_code)


def retry(f: Callable, excs, attempts: int = 3) -> Any:
    while True:
        try:
            return f()
        except excs:
            if attempts > 1:
                attempts -= 1
            else:
                raise


def make_full_url(config: BvDConfig, url: str) -> str:
    service_url = config.get('url', None)
    if service_url:
        return service_url + url

    raise BvDInvalidConfigException(400, 'Missing service url')


def make_headers(config: BvDConfig) -> Dict[str, str]:
    api_token = config.get('key', None)
    if api_token:
        return {
            'content-type': 'application/json',
            'apitoken': api_token,
        }

    raise BvDInvalidConfigException(400, 'Missing api token')


def send_request(config: BvDConfig, url: str, payload: Optional[dict]) -> List[CompanyRawData]:
    full_url = make_full_url(config, url)
    headers = make_headers(config)
    response = retry(
        lambda: post(full_url, headers=headers, json=payload, timeout=30),
        (RequestException, JSONDecodeError)
    )

    if response.status_code in {401, 403}:
        raise BvDAuthException(response.status_code, 'Failed to authorise for BvD request')

    if response.status_code >= 400:
        raise make_response_exception(response)

    result = response.json()
    if result is None or len(result) == 0:
        raise BvDEmptyResponseException(response.status_code, 'Received empty response from BvD')

    return result


def get_data(config: BvDConfig, bvd_ids: List[str], query: str) -> List[CompanyRawData]:
    return send_request(config, 'getdata', {
        'BvDIds': bvd_ids,
        'QueryString': query,
    })


def match(config: BvDConfig, criteria: MatchCriteria) -> List[CompanyRawData]:
    return send_request(config, 'match', criteria)


def get_query_string(name: str) -> str:
    query_file_path = join(dirname(dirname(abspath(__file__))), 'queries', name)
    with open(query_file_path, 'r') as file:
        return file.read().replace('\n', '')


def parse_demo_filename(filename: str) -> Optional[list]:
    name, ext = splitext(filename)
    if ext == '.json':
        components = name.split('_')
        if len(components) != 3:
            return None

        components.append(filename)
        return components

    return None


def get_demo_data(
    check: str = 'registry',
    country_code: str = None,
    bvd_id: str = None,
    company_number: str = None,
) -> dict:
    demo_files_path = join(dirname(dirname(abspath(__file__))), 'demo_data', check)
    _available_files = [parse_demo_filename(filename) for filename in listdir(demo_files_path)]
    available_files = [components for components in _available_files if components]

    if len(available_files) == 0:
        raise BvDServiceException(500, 'Missing demo files')

    demo_file_name = None
    # Attempt to find a match
    for demo_country_code, demo_bvd_id, demo_number, filename in available_files:
        if country_code and demo_country_code != country_code:
            continue
        if bvd_id and demo_bvd_id != bvd_id:
            continue
        if company_number and demo_number != company_number:
            continue
        demo_file_name = filename
        break

    if demo_file_name is None:
        # If no match return anything
        demo_file_name = cast(str, available_files[-1])

    with open(join(demo_files_path, demo_file_name), 'r') as file:
        return json.load(file)
