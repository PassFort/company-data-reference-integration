import logging
import re
from base64 import b64encode
from json import JSONDecodeError

import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

import xmltojson

from app.api.dowjones_region_codes import DJII_REGION_CODES
from app.api.types import (
    CountryMatchType,
    InputData,
    WatchlistAPICredentials,
    WatchlistAPIConfig,
)
from app.api.dowjones_types import (
    DataResults,
    SearchResults,
)

WATCHLIST_NOT_KNOWN_FILTER = 'NOTK'
WATCHLIST_ANY_FILTER = 'ANY'
WATCHLIST_NONE_FILTER = '-ANY'
WATCHLIST_NO_RCA_FILTER = '-23'
WATCHLIST_TRUE = 'true'
WATCHLIST_FALSE = 'false'


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
    def __init__(self, config: WatchlistAPIConfig, credentials: WatchlistAPICredentials):
        self.config = config
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
            f"{self.credentials.url.strip('/')}{route}",
            headers={
                'Authorization': f'Basic {self.auth_token}'
            },
            params=params,
        )
        resp.raise_for_status()
        return resp.text

    def search_params(self, input_data: InputData):
        params = {
            # Base params present for all searches
            'filter-sl-exclude-suspended': WATCHLIST_TRUE,
            'filter-ool-exclude-suspended': WATCHLIST_TRUE,
            'filter-oel-exclude-suspended': WATCHLIST_TRUE,

            # Params decided by integration config values
            'exclude-deceased': WATCHLIST_TRUE if self.config.ignore_deceased else WATCHLIST_FALSE,
            'filter-sic': WATCHLIST_ANY_FILTER if self.config.include_adverse_media else WATCHLIST_NONE_FILTER,
            'filter-pep-exclude-adsr': WATCHLIST_FALSE if self.config.include_adsr else WATCHLIST_TRUE,
            'filter-pep': WATCHLIST_ANY_FILTER if self.config.include_associates else WATCHLIST_NO_RCA_FILTER,
            'filter-ool': WATCHLIST_ANY_FILTER if self.config.include_ool else WATCHLIST_NONE_FILTER,
            'filter-oel': WATCHLIST_ANY_FILTER if self.config.include_oel else WATCHLIST_NONE_FILTER,
            'filter-region-keys': WATCHLIST_ANY_FILTER if not self.config.country_match_types else ','.join([
                str(CountryMatchType(match_type).to_dowjones_region_key())
                for match_type in self.config.country_match_types
            ]),
            'filter-sl': WATCHLIST_ANY_FILTER if self.config.sanctions_list_whitelist is None else
            WATCHLIST_NONE_FILTER if not self.config.sanctions_list_whitelist else
            ','.join(self.config.sanctions_list_whitelist),
            'search-type': self.config.search_type.lower(),
            'date-of-birth-strict': WATCHLIST_TRUE if self.config.strict_dob_search else WATCHLIST_FALSE,
        }

        # Params decided by check input data
        params['first-name'] = input_data.personal_details.name.given_names[0]
        params['surname'] = input_data.personal_details.name.family_name
        if len(input_data.personal_details.name.given_names) > 1:
            params['middle-name'] = ' '.join(input_data.personal_details.name.given_names[1:])
        if input_data.personal_details.dob is not None:
            params['date-of-birth'] = input_data.personal_details.dowjones_dob
        if input_data.personal_details.nationality is not None:
            params['filter-region'] = ','.join([
                WATCHLIST_NOT_KNOWN_FILTER,
                DJII_REGION_CODES[input_data.personal_details.nationality]
            ])

        return params

    def run_search(self, input_data: InputData):
        params = self.search_params(input_data)

        resp = self._get(
            '/search/person-name',
            params=params
        )

        results = SearchResults()
        return results.import_data(xmltojson.parse(resp))

    def fetch_data_record(self, peid):
        results = DataResults()
        results.import_data(xmltojson.parse(self._get(
            f'/data/records/{peid}',
            {'ame_article_type': 'all'},
        )))
        return results


DATA_RECORD_URL_PATTERN = re.compile('\/data\/records\/(.*)')


class DemoClient(APIClient):
    demo_name = None

    def extract_names(self, params):
        names = []
        if 'first-name' in params:
            names.append(params['first-name'])
        if 'middle-name' in params:
            names.append(params['middle-name'])
        if 'surname' in params:
            names.append(params['surname'])
        return ' '.join(names).lower()

    def set_demo_name(self, params):
        fullname = self.extract_names(params)
        if 'sanction' in fullname:
            self.demo_name = 'robert_mugabe'
        elif 'pep' in fullname:
            self.demo_name = 'david_cameron'
        elif 'media' in fullname:
            self.demo_name = 'hugo_chavez'
        elif fullname == 'bashar assad':
            self.demo_name = 'bashar_assad'
        elif fullname == 'hugo chavez':
            self.demo_name = 'hugo_chavez'
        elif fullname == 'robert mugabe':
            self.demo_name = 'robert_mugabe'
        elif fullname == 'david cameron':
            self.demo_name = 'david_cameron'

    def _get(self, route, params={}):
        is_search_req = route.startswith('/search/person-name')

        # Set demo for client when making initial search request
        if is_search_req:
            self.set_demo_name(params)

        # If not running a demo fallback to standard API client
        if self.demo_name is None:
            return APIClient._get(self, route, params)

        # Fetch data from file based on current demo and route hit
        if is_search_req:
            file_path = f'mock_data/search_results/{self.demo_name}.xml'
        else:
            matches = DATA_RECORD_URL_PATTERN.match(route)
            if matches and matches.group(1):
                file_path = f'mock_data/data_results/{self.demo_name}_{matches.group(1)}.xml'
            else:
                raise Exception(f'Mock file not found for route: "{route}"')

        with open(file_path, 'rb') as mock_data:
            return mock_data.read()
