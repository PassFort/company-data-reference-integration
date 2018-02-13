from unittest import TestCase
from unittest.mock import MagicMock, patch
from dassert import Assert

from app.utils import _get_pages, paginate


class TestGetPages(TestCase):

    def test_it_handles_whole_pages(self):
        pagination = {
            'limit': 20,
            'total': 60,
        }

        res = list(_get_pages(pagination))

        Assert.equal(res, [(20, 20), (40, 20)])

    def test_it_handles_half_pages(self):
        pagination = {
            'limit': 20,
            'total': 50,
        }

        res = list(_get_pages(pagination))

        Assert.equal(res, [(20, 20), (40, 20)])

    def test_it_handles_empty_pagination_object(self):
        res = list(_get_pages(None))

        Assert.equal(res, [])


class TestPaginate(TestCase):

    @patch('app.utils.base_request')
    def test_it_makes_multiple_requests(self, base_request_mock):
        pagination = {
            'limit': 20,
            'total': 60
        }

        paginate('', pagination, {})

        Assert.equal(base_request_mock.call_count, 2)
