import json
import logging
import requests
from json import JSONDecodeError

from pycountry import countries
from requests.adapters import ConnectTimeout, HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError
from requests.packages.urllib3.util.retry import Retry
from app.types import Error
from schematics.exceptions import DataError
from urllib.parse import quote

AUTH_URL = 'https://verisk-sso.okta.com/oauth2/aus6npp13bDEGCJju2p7/v1/token'


def requests_retry_session(
    retries=3, backoff_factor=0.3, session=None,
) -> requests.Session:
    _session = session or requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries, backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    _session.mount("https://", adapter)
    _session.timeout = 10
    return _session


class ApiClient():
    def __init__(self, client_id, client_secret, auth_url=AUTH_URL, is_demo=False, use_sandbox=False):
        if use_sandbox:
            self.url = 'https://boarding.g2netview.com/ebsvc/sandbox/v1'
        else:
            self.url = 'https://boarding.g2netview.com/ebsvc/v1'
        self.session = requests_retry_session()
        self.is_demo = is_demo
        self.auth_url = auth_url
        self.client_id = client_id
        self.client_secret = client_secret

    def _request(self, *args, **kwargs):
        errors = []
        try:
            response = self.session.request(*args, **kwargs)
            response.raise_for_status()
            data = response.json()
            return data, errors
        except ConnectionError as e:
            errors.append(Error.provider_connection_error(str(e)))
        except HTTPError as e:
            status_code = e.response.status_code
            if status_code > 499:
                errors.append(Error.provider_connection(str(e)))
            elif status_code in {403, 401}:
                errors.append(Error.provider_bad_credentials(str(e)))
            else:
                errors.append(Error.provider_unknown_error(str(e)))

        return None, errors

    def _get(self, *args, **kwargs):
        return self._request("GET", *args, **kwargs)

    def _post(self, *args, **kwargs):
        return self._request("POST", *args, **kwargs)

    def get_auth_token(self):
        response, errors = self._post(
            self.auth_url,
            data={
                "grant_type": "client_credentials",
                "client_id": self.client_id,
                "client_secret": self.client_secret,
            }
        )
        if errors:
            return None, errors
        token = response.get('access_token')
        if token:
            return token, []
        else:
            return None, [Error.provider_unknown_error("Error retrieving api access token")]
