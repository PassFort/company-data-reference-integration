import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from .api.match import TerminationInquiryRequest
from .auth.oauth import OAuth
import pprint


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


class MatchHandler():
    def __init__(self, pem_cert, consumer_key):
        self.base_url = 'https://sandbox.api.mastercard.com'
        self.oauth = OAuth(pem_cert, consumer_key)
        self.session = requests_retry_session()

    def prepare_request(self, url, method, body=None, params=None):
        auth_header = self.oauth.get_authorization_header(url, method, body, params)

        headers = {
            "Authorization": auth_header,
            "Accept": "application/json",
            "Content-Type": "application/json",
        }
        request = requests.Request(method, url, headers=headers, json=body, params=params)
        return request.prepare()

    def inquiry_request(self, body, page_offset=0, page_length=10):
        url = self.base_url + '/fraud/merchant/v3/termination-inquiry'
        params = {
            "PageOffset": page_offset,
            "PageLength": page_length,
        }

        inquiry_request_body = TerminationInquiryRequest().from_passfort(body).as_request_body()
        request = self.prepare_request(url, 'POST', body=inquiry_request_body, params=params)
        response = self.session.send(request)

        return response.json()
