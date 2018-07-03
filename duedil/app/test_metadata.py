import unittest
import os
import responses  # type: ignore
import requests
from schemad_types.utils import get_in

from flask import json
from app.metadata import get_metadata, request_phonenumbers, request_websites
from app.utils import tagged
from dassert import Assert

class TestMetadata(unittest.TestCase):
    base_url = "https://duedil.io/v4{}"

    def mock_get(self, url=None, **kwargs):
        responses.add(
            responses.GET,
            self.base_url.format(url),
            **kwargs
        )

    @responses.activate
    def test_it_requests_phone_numbers(self):
        url = "/company/gb/100/telephone-numbers.json"
        self.mock_get(url=url, json=create_telephone_response())

        request_phonenumbers('gb', '100', {})
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_always_limits_numbers_to_1(self):
        url = "/company/gb/100/telephone-numbers.json"
        self.mock_get(url=url, json=create_telephone_response())

        request_phonenumbers('gb', '100', {})
        Assert.in_('limit=1', responses.calls[0].request.url)

    @responses.activate
    def test_it_returns_a_single_phone_number(self):
        """
        Limits the pagination.

        This limit is because we currently only have the capability to store
        a single phone number on the check.
        """
        url = "/company/gb/100/telephone-numbers.json"
        self.mock_get(url=url, json=create_telephone_response())

        status_code, json = request_phonenumbers('gb', '100', {})
        phone_number = get_in(json, ['telephoneNumbers', 0, 'telephoneNumber'])
        Assert.equal("+44 20 3137 8490", phone_number)

    @responses.activate
    def test_it_handles_no_phonenumbers(self):
        url = "/company/gb/100/telephone-numbers.json"
        self.mock_get(url=url, json={'telephoneNumbers': []})

        status_code, json, = request_phonenumbers('gb', '100', {})
        phone_number = get_in(json, ['telephoneNumbers', 0, 'telephoneNumber'])
        Assert.equal(None, phone_number)

    @responses.activate
    def test_it_retries_phone_requests(self):
        url = "/company/gb/100/telephone-numbers.json"
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_telephone_response())

        request_phonenumbers('gb', '100', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_requests_websites(self):
        url = "/company/gb/100/websites.json"
        self.mock_get(url=url, json=create_website_response())

        request_websites('gb', '100', {})
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_always_limits_websites_to_1(self):
        url = "/company/gb/100/websites.json"
        self.mock_get(url=url, json=create_website_response())

        request_websites('gb', '100', {})
        Assert.in_('limit=1', responses.calls[0].request.url)

    @responses.activate
    def test_it_returns_a_single_website(self):
        """
        Limits the pagination.

        This limit is because we currently only have the capability to store
        a single website on the check.
        """
        url = "/company/gb/100/websites.json"
        self.mock_get(url=url, json=create_website_response())

        status_code, json = request_websites('gb', '100', {})
        website = get_in(json, ['websites', 0, 'website'])
        Assert.equal("http://www.duedil.com", website)

    @responses.activate
    def test_it_handles_no_websites(self):
        url = "/company/gb/100/websites.json"
        self.mock_get(url=url, json={'websites': []})

        status_code, json = request_websites('gb', '100', {})
        website = get_in(json, ['websites', 0, 'website'])

        Assert.equal(None, website)

    @responses.activate
    def test_it_retries_website_requests(self):
        url = "/company/gb/100/websites.json"
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_website_response())

        request_websites('gb', '100', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_structures_company_type(self):
        url = "/company/gb/100.json"
        self.mock_get(url=url, json=create_metadata_response())

        _, metadata = get_metadata('gb', '100', {})
        Assert.equal(metadata.structured_company_type.is_limited.v, True)
        Assert.equal(metadata.structured_company_type.is_public.v, False)


def create_metadata_response():
    with open("./demo_data/metadata.json", 'rb') as f:
        return json.loads(f.read())


def create_registry_response(with_pagination=False, pagination=None):
    with open("./demo_data/registry.json", 'rb') as f:
        return json.loads(f.read())


def create_telephone_response():
    with open("./demo_data/telephone.json", 'rb') as f:
        return json.loads(f.read())


def create_website_response():
    with open("./demo_data/website.json", 'rb') as f:
        return json.loads(f.read())
