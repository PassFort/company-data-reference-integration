import json
import logging
import requests
from json import JSONDecodeError

from pycountry import countries
from requests.adapters import ConnectTimeout, HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError
from requests.packages.urllib3.util.retry import Retry
from app.types import Error, ReportRequest, G2Report, PollRequest
from schematics.exceptions import DataError
from urllib.parse import quote
from schematics.exceptions import DataError

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


def headers_with_auth(token, **kwargs):
    return {**kwargs, 'Authorization': f'Bearer {token}'}


class ApiClient():
    def __init__(self, client_id=None, client_secret=None, use_sandbox=False, is_demo=False, auth_url=AUTH_URL):
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
                errors.append(Error.provider_connection_error(str(e)))
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

    def create_report(self, report_request: ReportRequest):
        token, errors = self.get_auth_token()
        if errors:
            return None, errors, None

        response, errors = self._post(
            self.url + '/newBoardingRequest',
            headers=headers_with_auth(token),
            json=report_request.input_data.as_request(),
        )

        if errors:
            return None, errors, response

        case_id = response.get('CaseID')
        if not case_id:
            err = 'Unexpected provider response - did not receive CaseId'
            logging.error(err)
            return None, [Error.provider_unknown_error(str(err))], response

        return {'case_id': case_id}, [], response

    def poll_report(self, poll_request: PollRequest):
        token, errors = self.get_auth_token()
        if errors:
            return None, errors, None

        response, errors = self._get(
            f'{self.url}/boardingRequestStatus/{poll_request.input_data.case_id}',
            headers=headers_with_auth(token),
        )
        if errors:
            return None, errors, response

        is_ready = response.get('ResponseReady')
        if is_ready is None:
            err = 'Unexpected provider response - did not receive ResponseReady'
            logging.error(err)
            return None, [Error.provider_unknown_error(str(err))], response

        return is_ready, [], response
