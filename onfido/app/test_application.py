import responses
import unittest
from onfido.mock_data.ekyc import mock_usa_check, mock_uk_check
from flask import json
from app.application import app
import json
from app.mock_data.mock_responses import mock_uk_matches, mock_usa_matches
from app.mock_data.mock_request import mock_request, mock_fail_applicant_response


class TestApplication(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.testing_app = app.test_client()

    @responses.activate
    def test_usa_applicant_check(self):
        self.maxDiff = None
        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants',
            json={
                'id': 'some_id',
                'country': 'usa',
            }
        )

        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants/some_id/checks',
            json=mock_usa_check['data'],
        )

        response = self.testing_app.post('/ekyc-check',
                                         data=json.dumps(mock_request),
                                         content_type='application/json',
                                         )
        json_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(mock_usa_matches, json_data['output_data']['matches'])

    @responses.activate
    def test_uk_applicant_check(self):
        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants',
            json={
                'id': 'some_id',
                'country': 'gbr',
            }
        )

        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants/some_id/checks',
            json=mock_uk_check['data'],
        )

        response = self.testing_app.post('/ekyc-check',
                                         data=json.dumps(mock_request),
                                         content_type='application/json',
                                         )
        json_data = json.loads(response.get_data(as_text=True))
        self.maxDiff = None
        self.assertEqual(mock_uk_matches, json_data['output_data']['matches'])

    @responses.activate
    def test_failed_applicant(self):
        expected_response = {'errors': [{'error': {'fields': {'dob': ['must be before 2018-02-25 00:00:00']},
                                                   'message': 'There was a validation error on this request',
                                                   'type': 'validation_error'}}], 'price': 0, 'raw': {'applicant': {
            'error': {'fields': {'dob': ['must be before 2018-02-25 00:00:00']},
                      'message': 'There was a validation error on this request', 'type': 'validation_error'}}}}
        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants',
            json=mock_fail_applicant_response,
            status=400,
        )

        response = self.testing_app.post('/ekyc-check',
                                         data=json.dumps(mock_request),
                                         content_type='application/json',
                                         )
        json_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(json_data, expected_response)

    @responses.activate
    def test_connection_error_on_check(self):
        expected_response = {'errors': [{'error': "Check creation request failed"}], 'price': 0,
                             'raw': {'applicant': {'id': 'some_id'}, 'check': 'Server returned 500 with no content.'}}
        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants',
            json={
                'id': 'some_id'
            }
        )
        responses.add(
            responses.POST,
            'https://api.onfido.com/v2/applicants/some_id/checks',
            status=500,
        )
        response = self.testing_app.post('/ekyc-check',
                                         data=json.dumps(mock_request),
                                         content_type='application/json',
                                         )
        json_data = json.loads(response.get_data(as_text=True))
        self.assertEqual(expected_response, json_data)
