from base64 import b64encode
from json import JSONDecodeError

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import xmltojson

from app.api.types import (
    InputData,
    WatchlistAPICredentials,
)
from app.api.dowjones_types import (
    SearchResults,
)

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


class APIClient():
    def __init__(self, credentials: WatchlistAPICredentials):
        self.credentials = credentials
        self.session = requests_retry_session()

    @property
    def auth_token(self):
        return b64encode(
            f'{self.credentials.namespace}/{self.credentials.username}:{self.credentials.password}'
            .encode('utf-8')
        ).decode('utf-8')

    def get(self, route, params):
        return self.session.get(
            f"{self.credentials.url}{route}",
            headers={
                'Authorization': f'Basic {self.auth_token}'
            },
            params=params,
        )

    def run_search(self, input_data: InputData):
        params = {
            'first-name': input_data.personal_details.name.given_names[0],
            'surname': input_data.personal_details.name.family_name
        }

        if len(input_data.personal_details.name.given_names) > 1:
            params['middle-name'] = input_data.personal_details.name.given_names[1:].join(' ')

        resp = self.get(
            '/search/person-name',
            params=params
        )

        results = SearchResults()
        return results.import_data(xmltojson.parse(resp.text))
