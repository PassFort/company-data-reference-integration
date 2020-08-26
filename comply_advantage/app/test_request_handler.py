"""
Integration tests for the request handler. A mix of requests that:
 - either call the provider and generate expected errors (e.g for bad authentication).
 - mock the expected response form the provider
"""

import json
import responses
import unittest
from unittest.mock import Mock, patch

from . import request_handler
from .request_handler import comply_advantage_search_request, get_result_by_search_ids
from .api.types import ScreeningRequestData, ComplyAdvantageConfig, ComplyAdvantageCredentials, ErrorCode
from .api.internal_types import ComplyAdvantageException, ComplyAdvantageSearchRequest
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

TEST_SCREENING_DATA_NATIONALITY = ScreeningRequestData({
    "entity_type": "INDIVIDUAL",
    "personal_details": {
        "name": {
            "family_name": "Hussein",
            "given_names": ["Hugo"]
        },
        "nationality": "zwe"
    }
})

TEST_SCREENING_DATA_BAD_NATIONALITY = ScreeningRequestData({
    "entity_type": "INDIVIDUAL",
    "personal_details": {
        "name": {
            "family_name": "Hussein",
            "given_names": ["Hugo"]
        },
        "nationality": "BAD_STRING"
    }
})

SEARCH_REQUEST_URL = 'https://api.complyadvantage.com/searches'


class TestHandleCallsPostCorrectly(unittest.TestCase):

    @patch.object(request_handler, 'requests_retry_session')
    def test_call_with_nationality(self, fake_retry):
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA_NATIONALITY, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))

        fake_retry().post.assert_called_with(
            'https://api.complyadvantage.com/searches?api_key=TEST',
            json={'search_term': 'Hugo Hussein', 'fuzziness': 0.5, 'filters': {
                'types': ['pep', 'sanction'], 'country_codes': ['ZW']
                }, 'share_url': True, 'offset': 0, 'limit': 100}
        )

    @patch.object(request_handler, 'requests_retry_session')
    def test_call_with_bad_nationality(self, fake_retry):
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA_BAD_NATIONALITY, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))

        fake_retry().post.assert_called_with(
            'https://api.complyadvantage.com/searches?api_key=TEST',
            json={'search_term': 'Hugo Hussein', 'fuzziness': 0.5, 'filters': {
                'types': ['pep', 'sanction'],
                }, 'share_url': True, 'offset': 0, 'limit': 100}
        )


class TestHandleSearchRequestErrors(unittest.TestCase):
    @responses.activate
    def test_provider_unreachable_returns_connection_error(self):
        # Not setting a response will make the unreachable
        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
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
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            credentials)
        self.assertEqual(result['errors'][0]['code'], ErrorCode.PROVIDER_UNKNOWN_ERROR.value)
        self.assertEqual(result['errors'][0]['info'], {'a': 'b'})

    @responses.activate
    def test_search_profile_missconfiguration_error(self):
        credentials = ComplyAdvantageCredentials({
            'api_key': 'TEST'
        })

        responses.add(
            responses.POST,
            SEARCH_REQUEST_URL,
            json={'message': 'Test bad request', 'errors': {'search_profile': 'is disabled for your account'}},
            status=400)

        result = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            credentials)

        self.assertEqual(result['errors'][0]['code'], ErrorCode.MISCONFIGURATION_ERROR.value)
        self.assertEqual(result['errors'][0]['info'], {'search_profile': 'is disabled for your account'})


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
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }), offset=0, limit=3)

        with self.subTest('Parses 3 responses'):
            self.assertEqual(len(result['raw']), 3)
            self.assertEqual(result["search_ids"], [81075653, 81076178, 81088222])

        result_from_non_paginated = comply_advantage_search_request(
            SEARCH_REQUEST_URL,
            ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }))

        with self.subTest('Parses 1 response'):
            self.assertEqual(len(result_from_non_paginated['raw']), 1)
            self.assertEqual(result_from_non_paginated["search_ids"], [81081935])

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
                ComplyAdvantageSearchRequest.from_input_data(TEST_SCREENING_DATA, ComplyAdvantageConfig()),
                ComplyAdvantageConfig(),
                ComplyAdvantageCredentials({
                    'api_key': 'TEST'
                }), offset=0, limit=3, max_hits=3)


class TestGetResults(unittest.TestCase):

    @responses.activate
    def test_returns_events_from_existing_searches(self):
        search_ids = []

        mock_response = get_response_from_file(f'paginate_test_full', folder='test_data')
        search_id = mock_response["content"]["data"]["id"]
        search_ids.append(search_id)
        responses.add(
            responses.GET, f'{SEARCH_REQUEST_URL}/{search_id}/details', json=mock_response
        )
        responses.add(
            responses.POST, f'{SEARCH_REQUEST_URL}', json=mock_response
        )

        with self.subTest('without adverse media'):
            result = get_result_by_search_ids(
                ComplyAdvantageConfig(),
                ComplyAdvantageCredentials({
                    'api_key': 'TEST'
                }),
                search_ids
            )

            self.assertEqual(result['errors'], [])
            self.assertEqual(len(result['events']), 7)

        with self.subTest('with adverse media'):
            result = get_result_by_search_ids(
                ComplyAdvantageConfig({
                    'include_adverse_media': True
                }),
                ComplyAdvantageCredentials({
                    'api_key': 'TEST'
                }),
                search_ids
            )

            self.assertEqual(result['errors'], [])
            self.assertEqual(len(result['events']), 9)


class TestFieldDefaultValue(unittest.TestCase):

    @responses.activate
    def test_field_default_value(self):
        search_ids = []

        mock_response = get_response_from_file(f'reproduce_default_value_error', folder='test_data')
        search_id = mock_response["content"]["data"]["id"]
        search_ids.append(search_id)
        responses.add(
            responses.GET, f'{SEARCH_REQUEST_URL}/{search_id}/details', json=mock_response
        )
        responses.add(
            responses.POST, f'{SEARCH_REQUEST_URL}', json=mock_response
        )

        result = get_result_by_search_ids(
            ComplyAdvantageConfig(),
            ComplyAdvantageCredentials({
                'api_key': 'TEST'
            }),
            search_ids
        )
        self.assertEqual(len(result['errors']), 0)
