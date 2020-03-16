import unittest

from app.api.types import (
    InputData,
    WatchlistAPIConfig,
    WatchlistAPICredentials,
)
from app.watchlist_client import DemoClient


DEFAULT_CONFIG = {
    "ignore_deceased": False,
    "include_adverse_media": True,
    "include_adsr": True,
    "include_associates": True,
    "include_oel": True,
    "include_ool": True,
    "search_type": "BROAD",
}

EXAMPLE_INPUT_DATA = {
    "entity_type": "INDIVIDUAL",
    "personal_details": {
        "name": {
            "given_names": ["David"],
            "family_name": "Cameron"
        },
    }
}


class TestConfigParams(unittest.TestCase):
    def test_ignore_deceased(self):
        with self.subTest("Defaults `exclude-deceased` to 'false'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['exclude-deceased'], 'false')

        with self.subTest("Can set `exclude-deceased` to 'true'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'ignore_deceased': True})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['exclude-deceased'], 'true')

    def test_include_adverse_media(self):
        with self.subTest("Defaults `filter-sic` to 'ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-sic'], 'ANY')

        with self.subTest("Can set `fitler-sic` to '-ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'include_adverse_media': False})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-sic'], '-ANY')

    def test_include_adsr(self):
        with self.subTest("Defaults `filter-pep-exclude-adsr` to 'false'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-pep-exclude-adsr'], 'false')

        with self.subTest("Can set `filter-pep-exclude-adsr` to 'true'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'include_adsr': False})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-pep-exclude-adsr'], 'true')

    def test_include_associates(self):
        # TODO: Optionally include associates (not a param?)
        pass

    def test_include_oel(self):
        with self.subTest("Defaults `filter-oel` to 'ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-oel'], 'ANY')

        with self.subTest("Can set `filter-oel` to '-ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'include_oel': False})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-oel'], '-ANY')

    def test_include_ool(self):
        with self.subTest("Defaults `filter-ool` to 'ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-ool'], 'ANY')

        with self.subTest("Can set `filter-ool` to '-ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'include_ool': False})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-ool'], '-ANY')

    def test_search_type(self):
        with self.subTest("Defaults `search-type` to 'broad'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['search-type'], 'broad')

        with self.subTest("Can set `search-type` to 'near'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'search_type': 'NEAR'})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['search-type'], 'near')

        with self.subTest("Can set `search-type` to 'precise'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'search_type': 'PRECISE'})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['search-type'], 'precise')
