import unittest
import responses  # type: ignore
import requests

from flask import json
from app.companies import request_company_search
from dassert import Assert


class TestShareholders(unittest.TestCase):
    base_url = "https://duedil.io/v4{}"

    def mock_post(self, url=None, **kwargs):
        responses.add(
            responses.POST,
            self.base_url.format(url),
            **kwargs
        )

    @responses.activate
    def test_it_makes_request_to_companies(self):
        url = "/search/companies.json?offset=0&limit=20"
        self.mock_post(url=url, json=create_companies_response())

        request_company_search('gb', 'test', {})
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_retries_companies_requests(self):
        url = "/search/companies.json?offset=0&limit=20"
        self.mock_post(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_post(url=url, json=create_companies_response())

        request_company_search('gb', 'test', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_formats_companies(self):
        url = "/search/companies.json?offset=0&limit=20"
        self.mock_post(url=url, json=create_companies_response())
        self.mock_post(url=url, json=create_companies_response())

        raw_companies, companies = request_company_search('gb', 'test', {})
        Assert.equal(len(companies), 2)
        Assert.equal(companies[0]['name'], 'Test Ltd')
        Assert.equal(companies[1]['number'], '09251990')
        Assert.equal(companies[0]['country'], 'GBR')


def create_companies_response():
    with open("./demo_data/companies.json", 'rb') as f:
        return json.loads(f.read())
