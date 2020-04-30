from json import JSONDecodeError

import requests
from app.api.errors import Error, MatchException
from app.api.match import (ContactDetails, InquiryResults,
                           TerminationInquiryRequest)
from app.auth.oauth import OAuth
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry


def requests_retry_session(
    retries=3, backoff_factor=0.3, session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries, backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.timeout = 10
    return session


class MatchHandler:
    def __init__(self, pem_cert, consumer_key):
        self.base_url = 'https://sandbox.api.mastercard.com/fraud/merchant/v3'
        self.oauth = OAuth(pem_cert, consumer_key)
        self.session = requests_retry_session()

    def fire_request(self, url, method, body=None, params=None):
        auth_header = self.oauth.get_authorization_header(
            url, method, body, params)

        headers = {
            'Authorization': auth_header,
            'Accept': 'application/json',
            'Content-Type': 'application/json',
        }
        response = self.session.request(
            method, url, headers=headers, json=body, params=params
        )
        if response.status_code != 200:
            if 'contact' in url and response.status_code == 400:
                pass
            else:
                raise MatchException(response)

        return response.json(), response.status_code

    def retro_inquiry_request(self, acquirer_id):
        url = self.base_url + '/retro/retro-list'
        body = {'RetroRequest': {'AcquirerId': acquirer_id}}

        response, _ = self.fire_request(url, 'POST', body=body)
        return response

    def retro_inquiry_details_request(self, acquirer_id, match_reference):
        url = self.base_url + '/retro/retro-inquiry-details'
        params = {
            "AcquirerId": acquirer_id
        }
        body = {
            "RetroInquiryRequest": match_reference
        }

        response, _ = self.fire_request(url, 'POST', json=body, params=params)
        response: InquiryResults = InquiryResults.from_match_response(response)

        return response.to_primitive()

    def contact_request(self, acquirer_id):
        url = self.base_url + '/common/contact-details'
        body = {'ContactRequest': {'AcquirerId': acquirer_id}}

        response, status_code = self.fire_request(url, 'POST', body=body)
        if status_code == 400:
            return None
        return response

    def join_contact_details(self, inquiry_results: InquiryResults):
        for match in inquiry_results.possible_merchant_matches:
            response = self.contact_request(match.added_by_aquirer_id)
            if response:
                match.add_contact_details(response)

    def inquiry_request(self, body, page_offset=0, page_length=10):
        url = self.base_url + '/termination-inquiry'
        params = {
            'PageOffset': page_offset,
            'PageLength': page_length,
        }

        inquiry_request_body = TerminationInquiryRequest().from_passfort(body).as_request_body()

        response, _ = self.fire_request(url, 'POST', body=inquiry_request_body, params=params)
        response: InquiryResults = InquiryResults.from_match_response(response)
        self.join_contact_details(response)

        while response.should_fetch_more():
            params['PageOffset'] += 1
            new_response, _ = self.fire_request(
                url, 'POST', body=inquiry_request_body, params=params
            )
            response.merge_data(new_response)
        return response.to_primitive()
