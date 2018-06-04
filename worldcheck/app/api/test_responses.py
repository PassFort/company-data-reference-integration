from unittest import TestCase

from swagger_client.models import Result, MatchStrength
from .types import WorldCheckConfig
from .responses import make_results_response, make_match_response


class ResultResponseTest(TestCase):
    def test_returns_all_matches_if_no_match_strength(self):
        result = make_results_response(results=[
            Result(reference_id='1', result_id='t1'),
            Result(match_strength=MatchStrength.WEAK, reference_id='2', result_id='t2'),
            Result(match_strength=MatchStrength.STRONG, reference_id='3', result_id='t3'),
            Result(match_strength='weird data', reference_id='4', result_id='t4'),
        ])
        self.assertEqual(len(result['raw']), 4)
        self.assertEqual(len(result['output_data']), 4)
        self.assertEqual(result['output_data'], [
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
        ])

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
                'match_id': '4',
            }
        ])
