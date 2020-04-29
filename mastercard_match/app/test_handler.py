import json
import unittest

import responses

from .api.passfort import InquiryRequest, MatchConfig, MatchCredentials
from .request_handler import MatchHandler

company_data = {
    "metadata": {
        "name": "Test",
        "addresses": [{
            "address": {
                "locality": "London",
                "country": "GBR",
                "route": "Elm street",
                "stree_number": "52",
            }
        }]
    },
    "associated_entities": [
        {
            "entity_type": "INDIVIDUAL",
            "personal_details": {
                "name": {
                    "family_name": "Bridges",
                    "given_names": ["Sam"],
                },
                "address_history": [
                    {
                        "address": {
                            "country": "GBR",
                            "locality": "London",
                            "route": "Princelet Stree",
                            "street_number": "11"
                        }
                    }
                ]
            },

        }
    ]
}


def load_cert():
    with open("test_data/test_api_key_sandbox_no_pass.pem", 'rb') as file:
        return file.read()


def load_file(path):
    with open(path, 'r') as file:
        return json.loads(file.read())


credentials = {
    "certificate": load_cert(),
    "consumer_key": "akey",
}
config = {
    "acquirer_id": '12345'
}


def paginated_request_callback(request):
    # have to do this as the first param which should be PageOffset
    # contains part of the url
    offset = next(v for k, v in request.params.items())
    body = load_file(f'test_data/paginate_test_{offset}.json')

    return 200, {}, json.dumps(body)


BASE_URL = 'https://sandbox.api.mastercard.com/fraud/merchant/v3'
INQUIRY_REQUEST_URL = f'{BASE_URL}/termination-inquiry'
CONTACT_REQUEST = f'{BASE_URL}/common/contact-details'


class TestHandler(unittest.TestCase):

    @responses.activate
    def test_paginated_request(self):
        responses.add_callback(
            responses.POST, INQUIRY_REQUEST_URL,
            callback=paginated_request_callback,
            content_type='application/json',
        )
        responses.add("POST", CONTACT_REQUEST, json={})
        request = InquiryRequest().import_data({
            "input_data": company_data,
            "credentials": credentials,
            "config": config
        }, apply_defaults=True)

        handler = MatchHandler(request.credentials.certificate, request.credentials.consumer_key)

        result = handler.inquiry_request(request, 0, 2)

        self.assertEqual(len(result['possible_merchant_matches']), 4)
