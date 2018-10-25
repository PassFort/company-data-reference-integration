"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response form the provider
"""

import json
import responses
import unittest


from .request_handler import comply_advantage_search_request
from .api.types import ScreeningRequestData, ComplyAdvantageConfig, ComplyAdvantageCredentials, ErrorCode
from .api.internal_types import ComplyAdvantageException
from .file_utils import get_response_from_file

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


def paginated_request_callback(request):
    payload = json.loads(request.body)

    # See if a non default limit was used
    if payload["limit"] != 100:
        resp_body = get_response_from_file(f'paginate_test_{payload["offset"]}', folder='test_data')
    else:
        resp_body = get_response_from_file(f'paginate_test_full', folder='test_data')
    return 200, {}, json.dumps(resp_body)


class TestPagination(unittest.TestCase):

    @responses.activate
    def test_can_paginate(self):
        responses.add_callback(
            responses.POST, SEARCH_REQUEST_URL,
            callback=paginated_request_callback,
            content_type='application/json',
        )

        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            TEST_SCREENING_DATA,
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }), offset=0, limit=3)

        with self.subTest('Parses 3 responses'):
            self.assertEqual(len(result['raw']), 3)

        result_from_non_paginated = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            TEST_SCREENING_DATA,
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))

        with self.subTest('Parses 1 response'):
            self.assertEqual(len(result_from_non_paginated['raw']), 1)

        with self.subTest('The 2 have the same number of events'):
            self.assertEqual(len(result['events']), len(result_from_non_paginated['events']))
            self.assertGreater(len(result['events']), 0)

    @responses.activate
    def test_raises_exception_if_max_hits_reached(self):
        responses.add_callback(
            responses.POST, SEARCH_REQUEST_URL,
            callback=paginated_request_callback,
            content_type='application/json',
        )

        with self.assertRaises(ComplyAdvantageException):
            comply_advantage_search_request(
                SEARCH_REQUEST_URL,
                TEST_SCREENING_DATA,
                ComplyAdvantageConfig(),
                ComplyAdvantageCredentials({
                    'api_key': 'TEST'
                }), offset=0, limit=3, max_hits=3)
