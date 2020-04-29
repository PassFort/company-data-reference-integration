from unittest import TestCase

from bvd.shareholders import Shareholder


class TestFormatShareholderData(TestCase):

    def test_handles_bad_input(self):
        bad_data_shareholder = {
            'full_name': 'MR HAL MALONE',
            'first_names': 'HAL',
            'last_name': 'MALONE',
            'type': 'One or more named individuals or families',
            'uci': '',
            'direct': 'NG',
            'total': 'n.a.',
            'country_code': 'n.a.',
            'state_code': None,
            'bvd_id': 'WW*4000000002483',
            'bvd9': '',
            'lei': None
        }
        formatted_shareholder = Shareholder.from_raw_data(bad_data_shareholder)
        self.assertEqual(formatted_shareholder.country_of_incorporation, None)
        self.assertEqual(formatted_shareholder.type.value, 'INDIVIDUAL')
        self.assertEqual(formatted_shareholder.first_names, 'HAL')
        self.assertEqual(formatted_shareholder.last_name, 'MALONE')
        self.assertEqual(formatted_shareholder.bvd_id, 'WW*4000000002483')
        self.assertEqual(formatted_shareholder.shareholdings, [])
