from unittest import TestCase

from app.worldcheck_handler import CaseHandler, MatchHandler
from app.api.types import WorldCheckCredentials, WorldCheckConfig

TEST_API_KEY = 'a4364e62-e58b-4b64-9c71-faead5417557'
TEST_API_SECRET = '/NoVqWHBRv23t5ae9OuQlODUX5yoAcJcFP8Z2nJldBkrsTCdqhRzGzrrTvD9EVqLgwTrXC4xKZ/Khfv6shMwAA=='
TEST_GROUP_ID = '418f28a7-b9c9-4ae4-8530-819c61b1ca6c'

PILOT_URL = 'https://rms-world-check-one-api-pilot.thomsonreuters.com/v1/'
GOOD_CREDENTIALS = {
    "api_key": TEST_API_KEY,
    "api_secret": TEST_API_SECRET,
    "is_pilot": True
}

PERSONAL_DETAILS_TM = {
    "name": {
        "v": {
            "given_names": ["Theresa"],
            "family_name": "May"
        }
    }
}


class CaseHandlerTest(TestCase):

    def test_filter_results(self):

        handler = CaseHandler(
            WorldCheckCredentials(GOOD_CREDENTIALS),
            WorldCheckConfig({
                'group_id': TEST_GROUP_ID,
                'minimum_match_strength': 'EXACT'
            }),
            is_demo=True
        )
        result = handler.get_results('lukoil_romania_srl_results')
        self.assertEqual(len(result['output_data']), 1)
        self.assertEqual(len(result['raw']), 3)


class CaseHandlerIntegrationTest(TestCase):
    def test_ongoing_monitoring_results_returns_data_from_worldcheck(self):
        test_query = "updateDate>='2018-06-27T00:00:00.00Z' and updateDate<'2018-06-29T00:00:00.00Z'"
        handler = CaseHandler(WorldCheckCredentials(GOOD_CREDENTIALS), None, False)

        # There should be 39 items in total for these 2 dates. Paginate by displaying 20 per page
        results = handler.parse_paginated_result(test_query, 20)

        self.assertEqual(len(results), 39)


class MatchHandlerTest(TestCase):

    def setUp(self):
        self.handler = MatchHandler(
            WorldCheckCredentials(GOOD_CREDENTIALS),
            WorldCheckConfig({
                'group_id': TEST_GROUP_ID
            }),
            is_demo=True
        )

    def test_get_match(self):
        with self.subTest('creates both a pep and a sanction event'):
            match_response = self.handler.get_entity_for_match('bashar_assad_152')
            self.assertEqual(len(match_response['events']), 2)

            pep_event = match_response['events'][0]
            sanction_event = match_response['events'][1]
            self.assertEqual(pep_event['event_type'], 'PEP_FLAG')
            self.assertEqual(sanction_event['event_type'], 'SANCTION_FLAG')

            with self.subTest('the pep event contains pep data and no sanctions'):
                self.assertEqual(pep_event['pep'], {
                    'match': True,
                    'roles': [{'name': 'President of the Syrian Arab Republic'}]
                })
                self.assertTrue('sanctions' not in pep_event)

            with self.subTest('the sanctions event contains sanctions and no pep data'):
                self.assertGreater(len(sanction_event['sanctions']), 0)
                self.assertTrue('pep' not in sanction_event)

        with self.subTest('creates a refer flag as default'):
            match_response = self.handler.get_entity_for_match('lukoil_romania_srl_2756289')
            self.assertEqual(len(match_response['events']), 1)
            self.assertEqual(match_response['events'][0]['event_type'], 'REFER_FLAG')

    def test_get_associates(self):
        self.assertDictEqual(
            self.handler.get_match_associates('lukoil_romania_srl_9437'),
            {
                'output_data': ['lukoil_romania_srl_2756289'],
                'errors': []
            })

    def test_get_associate_data(self):
        response = self.handler.get_associate('lukoil_romania_srl_9437',
                                              'lukoil_romania_srl_2756289')

        self.assertEqual(
            response['output_data'],
            {
                'name': 'LUKOIL ENERGY & GAS ROMANIA',
                'association': 'AFFILIATED_COMPANY',
                'is_pep': False,
                'is_sanction': False
            }
        )

