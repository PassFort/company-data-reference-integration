import unittest
import os
import responses  # type: ignore
import requests

from flask import json
from passfort_data_structure.companies.officers import Officer
from passfort_data_structure.entities.role import Role
from passfort_data_structure.entities.entity_type import EntityType
from app.officers import request_officers
from dassert import Assert


class TestOfficers(unittest.TestCase):
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
    def test_it_makes_request_to_officers(self):
        url = "/company/gb/100/officers.json"
        self.mock_get(url=url, json=create_officers_response())

        request_officers('gb', '100', {})
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_retries_officers_requests(self):
        url = "/company/gb/100/officers.json"
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_officers_response())

        request_officers('gb', '100', {})
        Assert.equal(len(responses.calls), 2)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_retries_officers_requests_in_pagination(self):
        url = "/company/gb/100/officers.json"
        self.mock_get(url=url, json=create_officers_response(with_pagination=True))
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json=create_officers_response())

        request_officers('gb', '100', {})
        Assert.equal(len(responses.calls), 4)
        Assert.in_(url, responses.calls[0].request.url)

    @responses.activate
    def test_it_makes_request_to_officers_with_pagination(self):
        self.mock_get(
            url="/company/gb/100/officers.json",
            json=create_officers_response(with_pagination=True)
        )

        request_officers('gb', '100', {})
        Assert.equal(len(responses.calls), 3)
        Assert.in_('offset=4&limit=4', responses.calls[1].request.url)
        Assert.in_('offset=8&limit=4', responses.calls[2].request.url)

    @responses.activate
    def test_it_handles_officers_requests_in_pagination_failing(self):
        url = "/company/gb/100/officers.json"
        self.mock_get(url=url, json=create_officers_response(with_pagination=True))
        self.mock_get(url=url, body=requests.exceptions.ConnectionError('Connection Refused'))
        self.mock_get(url=url, json={}, status=500)
        self.mock_get(url=url, json=create_officers_response(with_pagination=False))

        request_officers('gb', '100', {})
        Assert.equal(len(responses.calls), 5)

    @responses.activate
    def test_formats_officers(self):
        url = "/company/gb/100/officers.json"
        self.mock_get(url=url, json=create_officers_response())

        _, officers = request_officers('gb', '100', {})

        Assert.isinstance(officers[0], Officer)

        donald = officers[0]
        paul = officers[2]
        company = officers[3]

        with self.subTest('formats first_names from provided names'):
            Assert.equal(donald.first_names.v, 'Donald Andrew')
            Assert.equal(paul.first_names.v, 'Paul')
            Assert.equal(company.first_names, None)
            Assert.equal(company.last_name.v, "Turners Management Limited")

        with self.subTest('sets entity_type'):
            Assert.equal(donald.type.v, EntityType.INDIVIDUAL)
            Assert.equal(company.type.v, EntityType.COMPANY)

        with self.subTest('sets role'):
            Assert.equal(donald.role.v, Role.INDIVIDUAL_DIRECTOR)
            Assert.equal(company.role.v, Role.COMPANY_DIRECTOR)


def create_officers_response(with_pagination=False, pagination=None):
    with open("./demo_data/officers.json", 'rb') as f:
        data = json.loads(f.read())
        if with_pagination is False:
            data['pagination'] = None
        else:
            data['pagination'] = pagination or data['pagination']

        return data
