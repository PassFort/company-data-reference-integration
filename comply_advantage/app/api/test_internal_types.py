import unittest

from .internal_types import ComplyAdvantageResponse


def get_response_from_file(search_ref):
    import json
    with open(f'mock_data/{search_ref}.json', 'rb') as f:
        return json.loads(f.read())


class TestConvertDataToEvents(unittest.TestCase):

    def test_converts_to_expected_events(self):
        model = ComplyAdvantageResponse.from_json(get_response_from_file('bashar_assad'))
        events = model.to_validated_events()

        self.assertEqual(len(events), 1)

        actual_event = events[0]
        with self.subTest('returns match id'):
            self.assertEqual(actual_event['match_id'], '187844Z8P762UU0')

        with self.subTest('deduplicates and returns dates of birth'):
            self.assertEqual(sorted(actual_event['match_dates']), [
                "1960-10-24",
                "1965",
                "1965-09-11",
                "1966"
            ])

        with self.subTest('returns aliases and match name'):
            self.assertGreater(len(actual_event['aliases']), 0)

            # Check an alias that is different from the actual name
            self.assertTrue('Al Assad Bushra' in actual_event['aliases'])
            self.assertEqual(actual_event['match_name'], "Al Assad Bashar")
