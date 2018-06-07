from unittest import TestCase
from unittest.mock import MagicMock, patch
from dassert import Assert

from app.utils import _get_pages, paginate, string_compare


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


class TestStringCompare(TestCase):

    def test_it_handles_casing(self):
        self.assertTrue(string_compare('HELLO', 'Hello'))

    def test_it_handles_spacing(self):
        self.assertTrue(string_compare('hello world', 'hello world'))
        self.assertTrue(string_compare('hello world', 'hello\tworld'))

    def test_it_handles_special_characters(self):
        self.assertTrue(string_compare('hello\'s', 'hellos'))
        self.assertTrue(string_compare('h.ello.', 'hello'))

    def test_it_handles_hard_combinations(self):
        self.assertTrue(string_compare('^HELLo $ world\'s', 'hello worlds'))
