import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api.types import SearchInput, Error, CreditSafeAuthenticationError, CreditSafeSearchError

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


class CreditSafeHandler:

    def __init__(self, credentials):
        self.base_url = 'https://connect.creditsafe.com/v1'
        self.credentials = credentials
        self.session = requests_retry_session()

    def get_token(self, username, password):
        response = self.session.post(
            f'{self.base_url}/authenticate',
            json={
                'username': username,
                'password': password
            }
        )

        if response.status_code != 200:
            raise CreditSafeAuthenticationError(response)

        return response.json()['token']

    def search(self, input_data):
        # Valid for 1 hour. Multiple valid tokens can exist at the same time.
        token = self.get_token(self.credentials.username, self.credentials.password)

        queries = input_data.build_queries()

        companies = []
        raw = []

        for query in queries:
            url = f'{self.base_url}/companies?{query}&pageSize=20'
            response = self.session.get(
                url,
                headers={
                    'Content-Type': 'application/json',
                    'Authorization': f'Bearer {token}'
                })

            if response.status_code != 200 and len(companies) == 0:
                # Only raise the error if we didn't find any companies so far
                # E.g:
                # the name search returned results, but the regNo search errored, then
                # we are safe to ignore the error
                raise CreditSafeSearchError(response)

            result = response.json()
            raw.append(result)

            companies.extend(result.get('companies', []))
            if len(companies) >= 20:
                break
        return raw, companies
