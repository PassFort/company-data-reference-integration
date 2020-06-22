from unittest import TestCase
from passfort.cifas_check import OutputData
from cifas.search import FullSearchResponse, FullSearchResultItem, FullCaseDetail, BasicCaseDetail


def mock_get_codes(_):
    return {'123': 'PassFort'}


class TestCifasToPassFort(TestCase):
    def test_no_results(self):
        full_search_response = FullSearchResponse(
            MemberSearchReference='adsdadsadadad',
            FINDsearchReference=11323123123,
            FullSearchResult=[],
        )

        output_data = full_search_response.to_passfort_output_data({})
        self.assertEqual(str(full_search_response.FINDsearchReference), output_data.fraud_detection.search_reference)
        self.assertEqual(output_data.fraud_detection.match_count, 0)

    def test_some_results(self):
        full_search_response = FullSearchResponse(
            MemberSearchReference='adsdadsadadad',
            FINDsearchReference=11323123123,
            FullSearchResult=[
                FullSearchResultItem(FullCaseDetail=FullCaseDetail(
                    BasicCaseDetail=BasicCaseDetail(
                        CaseId=123,
                        OwningMember=123,
                        ManagingMember=123,
                        CaseType='AFR',
                        Product='BRKP',
                        DoNotFilter=True,
                        SupplyDate=None,
                        ApplicationDate=None,
                        ClaimDate=None,
                    ),
                    FilingReason=['UAC'],
                    LinkedCasesCount=0,
                    DeliveryChannel=None,
                    IPAddress=None,
                    Facility=None,
                )),
                FullSearchResultItem(FullCaseDetail=FullCaseDetail(
                    BasicCaseDetail=BasicCaseDetail(
                        CaseId=123,
                        OwningMember=123,
                        ManagingMember=123,
                        CaseType='AFR',
                        Product='BRKP',
                        DoNotFilter=True,
                        SupplyDate=None,
                        ApplicationDate=None,
                        ClaimDate=None,
                    ),
                    FilingReason=['UAC'],
                    LinkedCasesCount=0,
                    DeliveryChannel=None,
                    IPAddress=None,
                    Facility=None,
                )),
            ],
        )

        output_data = full_search_response.to_passfort_output_data(mock_get_codes)
        self.assertEqual(str(full_search_response.FINDsearchReference), output_data.fraud_detection.search_reference)
        self.assertEqual(output_data.fraud_detection.match_count, 2)
