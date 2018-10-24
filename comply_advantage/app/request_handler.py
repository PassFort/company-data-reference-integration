import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from simplejson import JSONDecodeError


from typing import TYPE_CHECKING
from .api.internal_types import ComplyAdvantageResponse
from .api.types import Error

if TYPE_CHECKING:
    from .api.types import ScreeningRequestData, ComplyAdvantageConfig, ComplyAdvantageCredentials


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.timeout = 10
    return session


def search_request(
        data: 'ScreeningRequestData',
        config: 'ComplyAdvantageConfig',
        credentials: 'ComplyAdvantageCredentials',
        is_demo=False):
    # TODO use proper mock data
    if is_demo:
        return {
            "output_data": {},
            "raw": {},
            "errors": [],
            "events": []
        }
    else:
        url = f'{credentials.base_url}/searches'
        return comply_advantage_search_request(url, data, config, credentials)


def comply_advantage_search_request(
        url: str,
        data: 'ScreeningRequestData',
        config: 'ComplyAdvantageConfig',
        credentials: 'ComplyAdvantageCredentials'):

    authorized_url = f'{url}?api_key={credentials.api_key}'

    # TODO paginate -> total_hits, offset, limit
    try:
        response = requests_retry_session().post(authorized_url, json=data.to_provider_format(config))
    except Exception as e:
        return {
            "errors": [Error.provider_connection_error(e)]
        }

    raw_response = {}
    errors = []
    try:
        raw_response = response.json()
    except JSONDecodeError:
        pass

    response_model = ComplyAdvantageResponse.from_json(raw_response)
    if response.status_code != 200:
        errors = [
            Error.from_provider_error(response.status_code, response_model.message, response_model.errors)
        ]

    return {
        "raw": raw_response,
        "errors": errors,
        "events": response_model.to_validated_events()
    }