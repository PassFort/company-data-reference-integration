import requests
from typing import TYPE_CHECKING
from .api.internal_types import ComplyAdvantageResponse

if TYPE_CHECKING:
    from .api.types import ScreeningRequestData, ComplyAdvantageConfig, ComplyAdvantageCredentials


def comply_advantage_search_request(
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

    url = f'{credentials.base_url}/searches?api_key={credentials.api_key}'

    # TODO add retry logic
    response = requests.post(url, json=data.to_provider_format(config))
    # TODO paginate -> total_hits, offset, limit
    # TODO parse response into events
    raw_response = response.json()
    response_model = ComplyAdvantageResponse().import_data(raw_response, apply_defaults=True)
    response_model.validate()
    return {
        "raw": raw_response,
        "errors": [],
        "events": [e.as_validated_json() for e in response_model.content.data.to_events()]
    }
