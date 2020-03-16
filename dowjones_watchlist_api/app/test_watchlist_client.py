import unittest

from app.api.types import (
    InputData,
    WatchlistAPIConfig,
    WatchlistAPICredentials,
)
from app.watchlist_client import DemoClient


DEFAULT_CONFIG = {
    'ignore_deceased': False,
    'include_adverse_media': True,
    'include_adsr': True,
    'include_associates': True,
    'include_oel': True,
    'include_ool': True,
    'search_type': 'BROAD',
}

EXAMPLE_INPUT_DATA = {
    'entity_type': 'INDIVIDUAL',
    'personal_details': {
        'name': {
            'given_names': ['David'],
            'family_name': 'Cameron'
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
        with self.subTest("Defaults `filter-pep` to 'ANY'"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-pep'], 'ANY')

        with self.subTest("Can set `filter-pep` to '-23'"):
            client = DemoClient(
                WatchlistAPIConfig(dict(DEFAULT_CONFIG, **{'include_associates': False})),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['filter-pep'], '-23')

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


class TestInputDataParams(unittest.TestCase):
    def test_names(self):
        with self.subTest("Sets `first-name` to first given name"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['first-name'], 'David')

        with self.subTest("Sets `surname` to family name"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertEqual(params['surname'], 'Cameron')

        with self.subTest("Does not set `middle-name` if none provided"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertNotIn('middle-name', params)

        with self.subTest("Sets `middle-name` to sum of all but the first of the given names"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(dict(EXAMPLE_INPUT_DATA, **{
                'personal_details': {
                    "name": {
                        "given_names": ["David", "Allen", "John"],
                        "family_name": "Cameron"
                    },
                }
            })))
            self.assertEqual(params['middle-name'], 'Allen John')

    def test_date_of_birth(self):
        with self.subTest("Does not set `date-of-birth` if none provided"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertNotIn('date-of-birth', params)

        with self.subTest("Sets `date-of-birth` if present"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData({
                'entity_type': 'INDIVIDUAL',
                'personal_details': {
                    'name': {
                        'given_names': ['David'],
                        'family_name': 'Cameron'
                    },
                    'dob': '1974-03-11'
                }
            }))
            self.assertEqual(params['date-of-birth'], '1974-03-11')

    def test_nationality(self):
        with self.subTest("Does not set `filter-region` if no nationality provided"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData(EXAMPLE_INPUT_DATA))
            self.assertNotIn('filter-region', params)

        with self.subTest("Can add nationality as DJII region code to `filter-region`"):
            client = DemoClient(
                WatchlistAPIConfig(DEFAULT_CONFIG),
                WatchlistAPICredentials()
            )
            params = client.search_params(InputData({
                'entity_type': 'INDIVIDUAL',
                'personal_details': {
                    'name': {
                        'given_names': ['David'],
                        'family_name': 'Cameron'
                    },
                    'nationality': 'JAM'
                }
            }))
            self.assertEqual(params['filter-region'], 'NOTK,JAMA')
