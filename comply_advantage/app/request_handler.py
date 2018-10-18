import requests
from typing import TYPE_CHECKING

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

    # TODO parse response into events
    return response.json()
