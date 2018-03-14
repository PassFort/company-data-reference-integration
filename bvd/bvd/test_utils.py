from unittest import TestCase
from mock import patch

from bvd.utils import send_request, BvDServiceException, match, BvDInvalidConfigException, get_data


class MockResponse:
    def __init__(self, json_data, status_code):
        self.json_data = json_data
        self.status_code = status_code

    def json(self):
        return self.json_data


credentials = {
    'url': 'http://api/',
    'key': 'myapikey',
}


class TestUtils(TestCase):

    def test_send_request(self):
        response = [{
            'NAME': 'Company name'
        }]

        bvd_exception_message = 'BvD Exception Message'

        exception_response = {
            'ExceptionMessage': bvd_exception_message,
        }

        with self.subTest('send expected request'):
            with patch('bvd.utils.post', side_effect=lambda *args, **kwargs: MockResponse(response, 200)) as mock_post:
                payload = {}
                endpoint = 'endpoint'
                retval = send_request(credentials, endpoint, payload)
                self.assertEqual(mock_post.call_count, 1)
                mock_post.assert_called_with(
                    credentials['url'] + endpoint,
                    headers={
                        'apitoken': credentials['key'],
                        'content-type': 'application/json',
                    },
                    json=payload,
                    timeout=30,
                )

                self.assertEqual(retval, response)

        with self.subTest('return full response for status_code < 400'):
            with patch('bvd.utils.post', side_effect=lambda *args, **kwargs: MockResponse(response, 304)) as mock_post:
                retval = send_request(credentials, 'endpoint', None)
                self.assertEqual(retval, response)

        with self.subTest('expect an error with default message'):
            with patch('bvd.utils.post', side_effect=lambda *args, **kwargs: MockResponse(None, 401)) as mock_post:
                with self.assertRaises(BvDServiceException):
                    send_request(credentials, 'endpoint', None)

        with self.subTest('expect an error with BvD provided message'):
            with patch('bvd.utils.post',
                       side_effect=lambda *args, **kwargs: MockResponse(exception_response, 403)) as mock_post:
                with self.assertRaises(BvDServiceException):
                    send_request(credentials, 'endpoint', None)

        with self.subTest('expect an exception if no service url is provided'):
            with patch('bvd.utils.post', side_effect=lambda: None):
                self.assertRaises(BvDInvalidConfigException, send_request, {
                    'key': 'key',
                }, 'endpoint', None)

        with self.subTest('expect an exception if no api token is provided'):
            with patch('bvd.utils.post', side_effect=lambda: None):
                self.assertRaises(BvDInvalidConfigException, send_request, {
                    'url': 'http://api/',
                }, 'endpoint', None)

    def test_match(self):
        empty_response = []
        criteria = {
            'Country': 'GBR',
            'Name': 'PassFort',
        }

        def mocked_send_request(*args, **kwargs):
            return 200, empty_response

        with self.subTest('send expected request'):
            with patch('bvd.utils.send_request', side_effect=mocked_send_request) as mock_send:
                status, retval = match(credentials, criteria)
                mock_send.assert_called_with(
                    credentials,
                    'match',
                    criteria,
                )

                self.assertEqual(status, 200)
                self.assertEqual(retval, empty_response)

    def test_get_data(self):
        empty_response = []
        query = 'NICE QUERY'

        def mocked_send_request(*args, **kwargs):
            return 200, empty_response

        with self.subTest('send expected request'):
            with patch('bvd.utils.send_request', side_effect=mocked_send_request) as mock_send:
                status, retval = get_data(credentials, ['BVDID'], query)
                mock_send.assert_called_with(
                    credentials,
                    'getdata',
                    {
                        'BvDIds': ['BVDID'],
                        'QueryString': query,
                    },
                )

                self.assertEqual(status, 200)
                self.assertEqual(retval, empty_response)
