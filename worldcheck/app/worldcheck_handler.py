from typing import Tuple, List

from swagger_client.models import NewCase, ProviderType, Case, Result, Filter
from app.auth import CustomAuthApiClient
from app.api.types import WorldCheckCredentials, WorldCheckConfig, ScreeningRequestData, Error
from app.api.responses import make_screening_started_response, make_screening_results_response

from swagger_client.api import CaseApi


class WorldCheckConnectionError(Exception):
    pass


class WorldCheckPendingError(Exception):
    pass


class CaseHandler:
    """
    Implements functionality to screen a new case and get the results of the screening
    """

    def __init__(self, credentials: WorldCheckCredentials, config: WorldCheckConfig):
        custom_client = CustomAuthApiClient(
            credentials.url,
            credentials.api_key,
            credentials.api_secret
        )
        self.api = CaseApi(custom_client)
        self.config = config

    def submit_screening_request(self, input_data: ScreeningRequestData):
        case = self._new_case(input_data)

        self.api.cases_case_system_id_screening_request_post(case.case_system_id)
        return make_screening_started_response(case.case_system_id)

    def get_results(self, case_system_id):
        audit_response = self.api.cases_case_system_id_audit_events_post(
            case_system_id,
            filter=Filter(query='actionType==SCREENED_CASE'))
        if audit_response.total_result_count == 0:
            raise WorldCheckPendingError()

        results = self.api.cases_case_system_id_results_get(case_system_id)
        return make_screening_results_response(results=results)

    def _new_case(self, input_data: ScreeningRequestData) -> Case:
        result = self.api.cases_post(
            NewCase(
                name=input_data.personal_details.name.combine(),
                provider_types=[ProviderType.WATCHLIST],
                entity_type=input_data.worldcheck_entity_type,
                group_id=self.config.group_id)
        )
        return result
