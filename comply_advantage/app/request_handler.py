import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


from typing import TYPE_CHECKING, List
from .api.internal_types import ComplyAdvantageResponse, ComplyAdvantageException, ComplyAdvantageMonitorResponse, \
    ComplyAdvantageSearchRequest
from .api.types import Error
from .file_utils import get_response_from_file

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
    if is_demo:
        return get_demo_data(data, config)
    else:
        url = f'{credentials.base_url}/searches'
        return comply_advantage_search_request(
            url,
            ComplyAdvantageSearchRequest.from_input_data(data, config),
            config,
            credentials
        )


def get_result_by_search_ids(
        config: 'ComplyAdvantageConfig',
        credentials: 'ComplyAdvantageCredentials',
        search_ids: List[int]):

    errors = []
    events = []
    session = requests_retry_session()
    try:
        if len(search_ids):
            url = f'{credentials.base_url}/searches/{search_ids[0]}?api_key={credentials.api_key}'
            response = session.get(url)

            errors = []
            raw_response, search_model = ComplyAdvantageResponse.from_raw(response)
            if response.status_code != 200 or search_model is None:
                errors.append(Error.from_provider_error(
                    response.status_code,
                    search_model and search_model.message,
                    search_model and search_model.errors))

    except Exception as e:
        errors = [Error.provider_connection_error(e)]

    session.close()

    if errors:
        return {
            'errors': errors,
            'events': events
        }
    else:
        # Run a new search, because the Comply Advantage api does not return the new entities otherwise
        # (to be fixed early 2019_
        return comply_advantage_search_request(
            f'{credentials.base_url}/searches',
            ComplyAdvantageSearchRequest.from_response_data(search_model.content.data),
            config,
            credentials
        )


def update_monitoring_request(
        credentials: 'ComplyAdvantageCredentials',
        search_ids: List[int],
        monitored: bool) -> dict:
    session = requests_retry_session()
    errors = []
    try:
        for search_id in search_ids:
            url = f'{credentials.base_url}/searches/{search_id}/monitors?api_key={credentials.api_key}'
            response = session.patch(url, json={"is_monitored": monitored})

            response_model = ComplyAdvantageMonitorResponse.from_json(response.json())
            if response.status_code != 200 or response_model.monitor_status != monitored:
                errors = [
                    Error.from_provider_error(response.status_code,
                                              f'Unable to update monitoring for {search_id}: {response_model.message}')
                ]
                break
    except Exception as e:
        errors = [Error.provider_connection_error(e)]

    session.close()
    return {
        "errors" : errors
    }


def comply_advantage_search_request(
        url: str,
        search_request_data: ComplyAdvantageSearchRequest,
        config: 'ComplyAdvantageConfig',
        credentials: 'ComplyAdvantageCredentials',
        offset=0,
        limit=100,
        max_hits=1000):

    authorized_url = f'{url}?api_key={credentials.api_key}'

    all_raw_responses = []
    all_events = []
    search_ids = []

    while offset < max_hits:
        try:
            session = requests_retry_session()
            response = session.post(
                authorized_url,
                json=search_request_data.paginate(offset, limit)
            )
        except Exception as e:
            return {
                "errors": [Error.provider_connection_error(e)]
            }
        finally:
            session.close()

        errors = []
        raw_response, response_model = ComplyAdvantageResponse.from_raw(response)
        if response.status_code != 200 or response_model is None:
            errors = [
                Error.from_provider_error(
                    response.status_code,
                    response_model and response_model.message,
                    response_model and response_model.errors)
            ]

        all_raw_responses.append(raw_response)
        all_events = all_events + response_model.to_validated_events(config)

        if response_model.search_id is not None:
            search_ids.append(response_model.search_id)

        offset = offset + limit

        if len(errors) > 0 or not response_model.has_more_pages():
            return {
                "search_ids": search_ids,
                "raw": all_raw_responses,
                "errors": errors,
                "events": all_events
            }

    raise ComplyAdvantageException(f"Reached max limit of hits to process - "
                                   f"{formatted_data}")


def get_demo_data(data: 'ScreeningRequestData', config: 'ComplyAdvantageConfig'):
    demo_name = data.search_term.lower().replace(' ', '_')
    try:
        raw_response = get_response_from_file(demo_name)
    except Exception:
        raw_response = {}

    response_model = ComplyAdvantageResponse.from_json(raw_response)
    return {
        "search_ids": [response_model.search_id],
        "raw": raw_response,
        "errors": [],
        "events": response_model.to_validated_events(config)
    }
