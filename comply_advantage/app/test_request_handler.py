"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response form the provider
"""

import responses
import unittest


from .request_handler import comply_advantage_search_request
from .api.types import ScreeningRequestData, ComplyAdvantageConfig, ComplyAdvantageCredentials, ErrorCode

TEST_SCREENING_DATA = ScreeningRequestData({
    "entity_type": "INDIVIDUAL",
    "personal_details": {
        "name": {
            "family_name": "Hussein",
            "given_names": ["Hugo"]
        }
    }
})

SEARCH_REQUEST_URL = 'https://api.complyadvantage.com/searches'


class TestHandleSearchRequestErrors(unittest.TestCase):

    def test_bad_key_resturns_configuration_error(self):
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            TEST_SCREENING_DATA,
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))
        self.assertEqual(result['errors'][0]['code'], ErrorCode.MISCONFIGURATION_ERROR.value)

    @responses.activate
    def test_provider_unreachable_returns_connection_error(self):
        # Not setting a response will make the unreachable
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            TEST_SCREENING_DATA,
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))
        self.assertEqual(result['errors'][0]['code'], ErrorCode.PROVIDER_CONNECTION_ERROR.value)

    @responses.activate
    def test_other_provider_error_response_returns_provider_error(self):
        credentials = ComplyAdvantageCredentials({
            'api_key': 'TEST'
        })
        responses.add(
            responses.POST,
            SEARCH_REQUEST_URL,
            json={'message': 'Test bad request', 'errors': {'a': 'b'}},
            status=400)
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            TEST_SCREENING_DATA,
            ComplyAdvantageConfig(),
            credentials)
        self.assertEqual(result['errors'][0]['code'], ErrorCode.PROVIDER_UNKNOWN_ERROR.value)
        self.assertEqual(result['errors'][0]['info'], {'a': 'b'})
