import logging
import re
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
    DataResults,
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

    def _get(self, route, params={}):
        resp = self.session.get(
            f"{self.credentials.url}{route}",
            headers={
                'Authorization': f'Basic {self.auth_token}'
            },
            params=params,
        )
        resp.raise_for_status()
        return resp.text

    def run_search(self, input_data: InputData):
        logging.info(f'Running search: {input_data.to_primitive()}')
        params = {
            'first-name': input_data.personal_details.name.given_names[0],
            'surname': input_data.personal_details.name.family_name
        }

        if len(input_data.personal_details.name.given_names) > 1:
            params['middle-name'] = ' '.join(input_data.personal_details.name.given_names[1:])

        resp = self._get(
            '/search/person-name',
            params=params
        )

        results = SearchResults()
        return results.import_data(xmltojson.parse(resp))

    def fetch_data_record(self, peid):
        logging.info(f'Fetching data record with PEID \'{peid}\'')
        results = DataResults()
        return results.import_data(xmltojson.parse(self._get(
            f'/data/records/{peid}',
            {'ame_article_type': 'all'},
        )))


DATA_RECORD_URL_PATTERN = re.compile('\/data\/records\/(.*)')


class DemoClient(APIClient):
    def _get(self, route, params={}):
        if route.startswith('/search/person-name'):
            file_path = f'mock_data/search_results/david_cameron.xml'
        else:
            matches = DATA_RECORD_URL_PATTERN.match(route)
            if matches and matches.group(1):
                file_path = f'mock_data/data_results/david_cameron_{matches.group(1)}.xml'
            else:
                raise Exception(f'Mock file not found for route: "{route}"')

        with open(file_path, 'rb') as mock_data:
            return mock_data.read()
