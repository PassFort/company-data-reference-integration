import unittest
import os
import responses  # type: ignore
import requests

from flask import json
from requests.exceptions import HTTPError
from passfort_data_structure.companies.ownership import Shareholder
from app.shareholders import request_shareholders
from app.utils import DueDilAuthException, DueDilServiceException
from dassert import Assert


class TestShareholders(unittest.TestCase):
    base_url = "https://duedil.io/v4{}"

    def mock_get(self, url=None, **kwargs):
        responses.add(
            responses.GET,
            self.base_url.format(url),
            **kwargs
        )

    def mock_post(self, url=None, **kwargs):
        """Mock out POST requests."""
        responses.add(
            responses.POST,
            self.base_url.format(url),
            **kwargs
        )

    @responses.activate
    def test_it_makes_request_to_shareholders(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json=create_shareholder_response())

        request_shareholders('gb', '100', {})
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_retries_shareholders_requests(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_shareholder_response())

        request_shareholders('gb', '100', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_makes_request_to_shareholders_with_pagination(self):
        self.mock_get(
            url="/company/gb/100/shareholders.json",
            json=create_shareholder_response(with_pagination=True)
        )

        request_shareholders('gb', '100', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_('offset=5&limit=5', responses.calls[1].request.url)

    @responses.activate
    def test_it_retries_shareholders_requests_in_pagination(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json=create_shareholder_response(with_pagination=True))
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_shareholder_response())

        request_shareholders('gb', '100', {})
        Assert.equal(len(responses.calls), 3)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_handles_shareholders_requests_in_pagination_failing(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json=create_shareholder_response(with_pagination=True))
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json={}, status=500)
        self.mock_get(url=url, json=create_shareholder_response(with_pagination=False))

        request_shareholders('gb', '100', {})
        Assert.equal(len(responses.calls), 4)

    @responses.activate
    def test_it_raises_on_401_status_code(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json={}, status=401)
        with self.assertRaises(DueDilAuthException):
            request_shareholders('gb', '100', {})

    @responses.activate
    def test_it_raises_on_403_status_code(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json={}, status=403)
        with self.assertRaises(DueDilAuthException):
            request_shareholders('gb', '100', {})

    @responses.activate
    def test_does_not_raise_on_404_status_code(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json={}, status=404)
        _, shareholders = request_shareholders('gb', '100', {})
        Assert.equal(shareholders, [])

    @responses.activate
    def test_it_raises_on_500_status_code(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json={}, status=500)
        with self.assertRaises(HTTPError):
            request_shareholders('gb', '100', {})

    @responses.activate
    def test_it_formats_shareholders(self):
        url = "/company/gb/100/shareholders.json"
        self.mock_get(url=url, json=create_shareholder_response(with_pagination=True))
        self.mock_get(url=url, json=create_shareholder_response(with_pagination=True, pagination={
            "limit": 5,
            "offset": 5,
            "total": 10
        }))

        raw_shareholders, shareholders = request_shareholders('gb', '100', {})
        Assert.equal(len(shareholders), 20)
        Assert.isinstance(shareholders[0], Shareholder)
        Assert.equal(shareholders[0].first_names.v, 'Henry Charles')
        Assert.equal(shareholders[2].last_name.v, 'Episode 1 Investments LP')
        Assert.equal(shareholders[0].shareholdings[0].v.share_class, 'Ordinary')
        Assert.equal(shareholders[0].shareholdings[0].v.currency, 'GBP')

        Assert.equal(round(shareholders[0].shareholdings[0].v.percentage, 4), round(0.337615283, 4))

        with self.subTest('formats nationality, dob and title for persons only'):
            Assert.equal(shareholders[0].dob.v.untrack(), '1991-08')
            Assert.equal(shareholders[0].nationality.v, 'GBR')
            Assert.equal(shareholders[0].title, 'Mr')

            Assert.is_(shareholders[2].dob, None)
            Assert.is_(shareholders[2].nationality, None)
            Assert.is_(shareholders[2].title, None)

        with self.subTest('formats company id and country of incorporation for companies only'):
            Assert.equal(shareholders[0].company_number, None)
            Assert.equal(shareholders[0].country_of_incorporation, None)

            Assert.equal(shareholders[2].company_number, 'LP015401')
            Assert.equal(shareholders[2].country_of_incorporation, 'GBR')


def create_registry_response(with_pagination=False, pagination=None):
    with open("./demo_data/registry.json", 'rb') as f:
        return json.loads(f.read())


def create_officers_response(with_pagination=False, pagination=None):
    with open("./demo_data/officers.json", 'rb') as f:
        data = json.loads(f.read())
        if with_pagination is False:
            data['pagination'] = None
        else:
            data['pagination'] = pagination or data['pagination']

        return data


def create_shareholder_response(with_pagination=False, pagination=None):
    with open("./demo_data/shareholders.json", 'rb') as f:
        data = json.loads(f.read())
        if with_pagination is False:
            data['pagination'] = None
        else:
            data['pagination'] = pagination or data['pagination']

        return data


def create_telephone_response():
    with open("./demo_data/telephone.json", 'rb') as f:
        return json.loads(f.read())


def create_website_response():
    with open("./demo_data/website.json", 'rb') as f:
        return json.loads(f.read())
