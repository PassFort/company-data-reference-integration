from unittest import TestCase
from passfort.cifas_check import OutputData
from cifas.search import FullSearchResponse, FullSearchResultItem


class TestCifasToPassFort(TestCase):
    def test_no_results(self):
        full_search_response = FullSearchResponse(
            MemberSearchReference='adsdadsadadad',
            FINDsearchReference=11323123123,
            FullSearchResult=[],
        )

        output_data = full_search_response.to_passfort_output_data()
        self.assertEqual(str(full_search_response.FINDsearchReference), output_data.fraud_detection.search_reference)
        self.assertEqual(output_data.fraud_detection.match_count, 0)

    def test_some_results(self):
        full_search_response = FullSearchResponse(
            MemberSearchReference='adsdadsadadad',
            FINDsearchReference=11323123123,
            FullSearchResult=[
                FullSearchResultItem(),
                FullSearchResultItem(),
            ],
        )

        output_data = full_search_response.to_passfort_output_data()
        self.assertEqual(str(full_search_response.FINDsearchReference), output_data.fraud_detection.search_reference)
        self.assertEqual(output_data.fraud_detection.match_count, 2)
