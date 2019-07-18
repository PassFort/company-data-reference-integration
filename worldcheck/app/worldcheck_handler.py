from swagger_client.models import NewCase, ProviderType, Case, CaseEntityType, Result, Filter, Field, MatchStrength
from app.auth import CustomAuthApiClient
from app.api.types import WorldCheckCredentials, WorldCheckConfig, ScreeningRequestData, Error
from app.api.responses import make_screening_started_response, make_results_response, make_match_response, \
    make_associate_response, make_associates_response
from swagger_client.api import CaseApi, ReferenceApi

import logging
import errno

from app.utils import create_response_from_file


class WorldCheckConnectionError(Exception):
    pass


class WorldCheckPendingError(Exception):
    pass


class CaseHandler:
    """
    Implements functionality to screen a new case and get the results of the screening
    """

    def __init__(self, credentials: WorldCheckCredentials, config: WorldCheckConfig, is_demo=False):
        custom_client = CustomAuthApiClient(
            credentials.url,
            credentials.api_key,
            credentials.api_secret
        )
        self.case_api = CaseApi(custom_client)
        self.config = config
        self.is_demo = is_demo

    def submit_screening_request(self, input_data: ScreeningRequestData):
        if self.is_demo:
            case_system_id = input_data.name.lower().replace(" ", "_") + "_results"
        else:
            case = self.__new_case(input_data)
            self.case_api.cases_case_system_id_screening_request_post(case.case_system_id)
            case_system_id = case.case_system_id
        return make_screening_started_response(case_system_id)

    def get_results(self, case_system_id):
        if self.is_demo:
            try:
                results = self.case_api.api_client.deserialize(
                    create_response_from_file("./mock_data/{}.json".format(case_system_id)),
                    'list[Result]'
                )
            except FileNotFoundError:
                results = []
            except OSError as os_ex:
                if os_ex.errno == errno.ENAMETOOLONG:
                    logging.error("Demo institution queried WorldCheck with too long a profile name")
                    results = []
                else:
                    raise

        else:
            audit_response = self.case_api.cases_case_system_id_audit_events_post(
                case_system_id,
                filter=Filter(query='actionType==SCREENED_CASE'))
            if audit_response.total_result_count == 0:
                raise WorldCheckPendingError()

            results: list[Result] = self.case_api.cases_case_system_id_results_get(case_system_id)

        return make_results_response(results=results, config=self.config)

    def set_ongoing_screening(self, case_system_id):
        if self.is_demo:
            pass
        else:
            self.case_api.cases_case_system_id_ongoing_screening_put(case_system_id)

    def disable_ongoing_screening(self, case_system_id):
        if self.is_demo:
            pass
        else:
            self.case_api.cases_case_system_id_ongoing_screening_delete(case_system_id)

    def get_ongoing_screening_results(self, from_date):
        iso_dt = from_date.strftime('%Y-%m-%dT%H:%M:%S.%fZ')

        return self.parse_paginated_result(f"updateDate>='{iso_dt}'", 100)

    def parse_paginated_result(self, query, items_per_page):
        from swagger_client.models import OngoingScreeningUpdateSearchResponse, Pagination
        updated_result_ids = []
        current_page = 1
        while True:
            raw_result: OngoingScreeningUpdateSearchResponse = self.case_api.cases_ongoing_screening_updates_post(
                filter=Filter(
                    query=query,
                    pagination=Pagination(current_page=current_page, items_per_page=items_per_page)
                ))

            if len(raw_result.results) == 0:
                return updated_result_ids

            updated_result_ids.extend([r.case_system_id for r in raw_result.results])
            current_page += 1

    def __new_case(self, input_data: ScreeningRequestData) -> Case:
        result = self.case_api.cases_post(
            NewCase(
                name=input_data.name,
                provider_types=[ProviderType.WATCHLIST],
                entity_type=input_data.worldcheck_entity_type,
                group_id=self.config.group_id)
        )

        return result

    @staticmethod
    def __secondary_fields(input_data: ScreeningRequestData):
        fields = []
        if input_data.worldcheck_entity_type == CaseEntityType.INDIVIDUAL:
            if input_data.personal_details.gender and input_data.personal_details.gender.v:
                fields.append(
                    Field(type_id="SFCT_1",
                          value=input_data.personal_details.gender.wordlcheck_gender))
            if input_data.personal_details.dob and input_data.personal_details.dob.v:
                fields.append(
                    Field(type_id="SFCT_2",
                          date_time_value=input_data.personal_details.dob.v))
            if input_data.personal_details.nationality and input_data.personal_details.nationality.v:
                fields.append(
                    Field(type_id="SFCT_5",
                          value=input_data.personal_details.nationality.v))
        else:
            if input_data.metadata.country_of_incorporation and \
                    input_data.metadata.country_of_incorporation.v:
                fields.append(
                    Field(type_id="SFCT_6",
                          value=input_data.metadata.country_of_incorporation.v))
        return fields


class MatchHandler:

    def __init__(self, credentials: WorldCheckCredentials, config: WorldCheckConfig, is_demo=False):
        custom_client = CustomAuthApiClient(
            credentials.url,
            credentials.api_key,
            credentials.api_secret
        )
        self.ref_api = ReferenceApi(custom_client)
        self.config = config
        self.is_demo = is_demo

    def get_entity_for_match(self, match_id):
        entity = self.__get_entity(match_id)
        return make_match_response(
            result=entity,
            associate_relationships=[
                {
                    'associate_id': a.target_entity_id,
                    'association': a.type
                } for a in entity.associates or []
            ]
        )

    # TO BE DEPRECATED
    def get_match_associates(self, match_id):
        from swagger_client.models import Entity
        entity: Entity = self.__get_entity(match_id)
        return make_associates_response([a.target_entity_id for a in entity.associates or []])

    # TO BE DEPRECATED
    def get_associate_old(self, match_id, associate_id):
        from swagger_client.models import Entity
        matched_entity: Entity = self.__get_entity(match_id)
        associated_entity = self.__get_entity(associate_id)

        association_data = next(a for a in matched_entity.associates if a.target_entity_id == associate_id)
        return make_associate_response(associated_entity, association_data.type)

    def get_associate(self, associate_id, association):
        associated_entity = self.__get_entity(associate_id)

        return make_associate_response(associated_entity, association)

    def __get_entity(self, match_id):
        import datetime
        n = datetime.datetime.now()

        if self.is_demo:
            entity = self.ref_api.api_client.deserialize(
                create_response_from_file("./mock_data/{}.json".format(match_id)),
                'IndividualEntity'
            )
        else:
            entity = self.ref_api.reference_profile_id_get(match_id)

        delta = datetime.datetime.now() - n
        logging.info('Time to retrieve entity {}: {}'.format(match_id, delta))

        return entity
