from unittest import TestCase

from app.worldcheck_handler import CaseHandler
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
