import os
import logging
import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from app.api.models import GeoCodingCheck, GeoCodingResponse, LoqateAddress, PassFortAddress
from app.api.error import Error
from .demo_data import get_demo_result


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


def maybe_get_error(json_data):
    if not isinstance(json_data, dict):
        return None

    error_number = json_data.get('Number')
    if not error_number:
        return None

    if error_number in [1, 2, 3, 4, 6, 15, 16]:
        return Error.provider_misconfiguration_error(json_data['Cause'])
    else:
        return Error.provider_unknown_error(json_data['Cause'])

class RequestHandler():

    def __init__(self):
        self.url = "https://api.addressy.com/Cleansing/International/Batch/v1.00/json4.ws"
        self.session: requests.Session = requests_retry_session()

    def call_geocoding_api(self, body):
        response = self.session.request('POST', self.url, json=body)

        return response.json()

    def handle_geocoding_check(self, data: GeoCodingCheck):
        if data.is_demo:
            return get_demo_result(data)
        request_body = data.to_request_body()

        raw = self.call_geocoding_api(request_body)

        maybe_error = maybe_get_error(raw)
        if maybe_error:
            logging.error(maybe_error)
            return {
                'errors': [maybe_error],
                'raw': raw,
            }

        geocoding_response = GeoCodingResponse.from_raw(raw)

        passfort_address = PassFortAddress.from_loqate(geocoding_response.geocoding_match)
        geocoding_accuracy = geocoding_response.geocoding_match.get_geo_accuracy()

        result = {
            "output_data": {
                "address": passfort_address.to_primitive(),
                "metadata": {
                    'geocode_accuracy': geocoding_accuracy
                },
            },
            "raw": raw
        }

        return result

