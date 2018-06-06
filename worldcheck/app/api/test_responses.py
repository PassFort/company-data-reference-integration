from unittest import TestCase

from swagger_client.models import Result, MatchStrength
from .types import WorldCheckConfig
from .responses import make_results_response, make_match_response

ALL_MATCH_IDS = [
    {
        'match_id': '1',
    },
    {
        'match_id': '2',
    },
    {
        'match_id': '3',
    },
    {
        'match_id': '4',
    }
]


class ResultResponseTest(TestCase):

    @staticmethod
    def make_response_with_config(config):
        return make_results_response(results=[
            Result(reference_id='1', result_id='t1'),
            Result(match_strength=MatchStrength.WEAK, reference_id='2', result_id='t2'),
            Result(match_strength=MatchStrength.STRONG, reference_id='3', result_id='t3'),
            Result(match_strength='weird data', reference_id='4', result_id='t4'),
        ], config=config)

    def assert_all_matches_returned(self, result):
        self.assertEqual(len(result['raw']), 4)
        self.assertEqual(len(result['output_data']), 4)
        self.assertEqual(result['output_data'], ALL_MATCH_IDS)

    def test_returns_all_matches(self):

        with self.subTest('if there is no config'):
            result = self.make_response_with_config(None)
            self.assert_all_matches_returned(result)

        with self.subTest('if there is no minimum_match_strength'):
            result = self.make_response_with_config(WorldCheckConfig({
                'group_id': 'xyz'
            }))
            self.assert_all_matches_returned(result)

        with self.subTest('if there is an unexpected minimum_match_strength'):
            result = self.make_response_with_config(WorldCheckConfig({
                'group_id': 'xyz',
                'minimum_match_strength': 'Say what?'
            }))
            self.assert_all_matches_returned(result)

    def test_returns_results_filtered_by_match_strength(self):
        result = make_results_response(results=[
            Result(reference_id='1', result_id='t1'),
            Result(match_strength=MatchStrength.WEAK, reference_id='2', result_id='t2'),
            Result(match_strength=MatchStrength.STRONG, reference_id='3', result_id='t3'),
            Result(match_strength='weird data', reference_id='4', result_id='t4'),
        ], config=WorldCheckConfig({
            'group_id': 'xyz',
            'minimum_match_strength': 'MEDIUM'
        }))
        self.assertEqual(len(result['raw']), 4)
        self.assertEqual(len(result['output_data']), 3)
        self.assertEqual(result['output_data'], [
            {
                'match_id': '1',
            },
            {
                'match_id': '3',
            },
            {
                'match_id': '4',  # The unexpected match strength
            }
        ])
