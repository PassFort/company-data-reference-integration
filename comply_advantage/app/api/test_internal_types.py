import unittest

from .internal_types import ComplyAdvantageResponse, ComplyAdvantageConfig
from ..file_utils import get_response_from_file


class TestConvertDataToEvents(unittest.TestCase):

    def test_converts_to_expected_events(self):
        model = ComplyAdvantageResponse.from_json(get_response_from_file('bashar_assad'))
        events = model.to_validated_events(ComplyAdvantageConfig())

        self.assertEqual(len(events), 2)

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

        with self.subTest('returns associates'):
            self.assertEqual(
                sorted(actual_event['associates'], key=lambda x: x['name'])[0]['name'],
                'Asma al-Assad')

        with self.subTest('is not deceased'):
            self.assertNotIn('deceased', actual_event)
            self.assertNotIn('deceased_dates', actual_event)

        chavez_model = ComplyAdvantageResponse.from_json(get_response_from_file('hugo_chavez'))
        chavez_events = chavez_model.to_validated_events(ComplyAdvantageConfig())

        with self.subTest('returns a deceased match'):
            self.assertTrue(any([
                event.get('deceased') and event['deceased_dates'] == ['2013-03-05']
                for event in chavez_events
            ]))

        with self.subTest('returns other details'):
            self.assertEqual(len(actual_event['details']), 1)  # Only 1, as they are grouped by name
            self.assertEqual(actual_event['details']['title'], 'Related Url')
