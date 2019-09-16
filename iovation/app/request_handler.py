import requests

from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from .api.types import CreditSafeAuthenticationError, CreditSafeSearchError, CreditSafeReportError
from .api.internal_types import CreditSafeCompanySearchResponse, CreditSafeCompanyReport


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


class IovationHandler:

    def __init__(self, credentials, test_env=True):
        if test_env:
            self.base_url = 'https://ci-api.iovation.com/fraud/v1'
        else:
            self.base_url = 'https://api.iovation.com/fraud/v1'
        self.credentials = credentials
        self.session = requests_retry_session()

    def run_check(self, input_data):
        # TODO
        pass
