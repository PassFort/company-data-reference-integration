import json
import logging
import requests
from json import JSONDecodeError

from pycountry import countries
from requests.adapters import HTTPAdapter
from requests.exceptions import ConnectionError, HTTPError
from requests.packages.urllib3.util.retry import Retry
from schematics.exceptions import DataError

from app.bvd.datasets import DataSet
from app.bvd.types import (
    AddToRecordSetResult,
    CreateRecordSetResult,
    DataResult,
    FetchUpdatesResult,
    OwnershipResult,
    RegistryResult,
    SearchResult,
)
from app.passfort.types import Error


def search_demo(name=None, country=None, state=None, company_number=None):
    search_query = (name or "").lower()
    if "fail" in search_query:
        return "demo_data/search/fail.json"
    elif "partial" in search_query:
        return f"demo_data/search/partial.json"
    else:
        return f"demo_data/search/pass.json"


def demo_path(check_type, bvd_id=None):
    if bvd_id == "fail":
        return f"demo_data/{check_type}/fail.json"
    elif bvd_id == "partial":
        return f"demo_data/{check_type}/partial.json"
    else:
        return f"demo_data/{check_type}/pass.json"


def country_alpha_3_to_2(alpha_3):
    try:
        return countries.get(alpha_3=alpha_3).alpha_2
    except (LookupError, AttributeError):
        logging.error(f"Received invalid alpha 3 code from PassFort {alpha_3}")
        return None


def prune_nones(value):
    if isinstance(value, dict):
        return {k: prune_nones(v) for k, v in value.items() if v is not None}
    if isinstance(value, list):
        return [prune_nones(v) for v in value]
    else:
        return value


def requests_retry_session(
    retries=3, backoff_factor=0.3, session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries, read=retries, connect=retries, backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount("https://", adapter)
    session.timeout = 10
    return session


class Client:
    def __init__(self, token, demo):
        self.token = token
        self.demo = demo
        self.session = requests_retry_session()
        self.base_url = "https://Orbis.bvdinfo.com/api/orbis"
        self.raw_responses = []
        self.errors = []

    def _record_error(self, error, **kwargs):
        self.errors.append(error.to_primitive())
        logging.error({**error.to_primitive(), **kwargs})

    def _request(self, response_model, get_demo_data, *args, **kwargs):
        try:
            if self.demo:
                with open(get_demo_data()) as demo_data:
                    data = json.load(demo_data)
            else:
                response = self.session.request(*args, **kwargs,)
                response.raise_for_status()
                data = response.json()

            self.raw_responses.append(data)

        except ConnectionError as e:
            self._record_error(Error.provider_connection(str(e)))
            data = {}
        except HTTPError as e:
            if e.response.status_code > 499:
                self._record_error(Error.provider_connection(str(e)))
            else:
                self.raw_responses.append(e.response.text)
                self._record_error(Error.provider_unknown_error(str(e)))
            data = {}
        except JSONDecodeError as e:
            self._record_error(Error.bad_provider_response(str(e)))
            data = {}

        try:
            model = response_model().import_data(prune_nones(data), apply_defaults=True)
            model.validate()
            return model
        except DataError as e:
            self._record_error(Error.bad_provider_response(e.to_primitive()), json=data)
            logging.error(
                {
                    "message": "provider response did not match expectation",
                    "cause": e.to_primitive(),
                }
            )

        return None

    def _get(self, response_model, get_demo_data, *args, **kwargs):
        return self._request(response_model, get_demo_data, "GET", *args, **kwargs)

    def _post(self, response_model, get_demo_data, *args, **kwargs):
        return self._request(response_model, get_demo_data, "POST", *args, **kwargs)

    def _put(self, response_model, get_demo_data, *args, **kwargs):
        return self._request(response_model, get_demo_data, "PUT", *args, **kwargs)

    def search(self, name=None, country=None, state=None, company_number=None):
        return self._get(
            SearchResult,
            lambda: search_demo(name, country, state, company_number),
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {
                        "WHERE": [
                            {
                                "MATCH": {
                                    "Criteria": {
                                        key: value
                                        for key, value in {
                                            "Name": name,
                                            "NationalId": company_number,
                                            "Country": country_alpha_3_to_2(country),
                                            "State": state,
                                        }.items()
                                        if value is not None
                                    }
                                }
                            }
                        ],
                        "SELECT": [
                            "BVDID",
                            "MATCH.BVD9",
                            "MATCH.NAME",
                            "MATCH.STATUS",
                            "MATCH.NAME_INTERNATIONAL",
                            "MATCH.ADDRESS",
                            "MATCH.POSTCODE",
                            "MATCH.CITY",
                            "MATCH.COUNTRY",
                            "MATCH.NATIONAL_ID",
                            "MATCH.STATE",
                            "MATCH.ADDRESS_TYPE",
                            "MATCH.HINT",
                            "MATCH.SCORE",
                        ],
                    }
                )
            },
        )

    def _fetch_data(self, response_model, get_demo_data, bvd_id, data_set=DataSet.ALL):
        return self._get(
            response_model,
            get_demo_data,
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {"WHERE": [{"BvDID": bvd_id}], "SELECT": data_set.fields}
                )
            },
        )

    def fetch_company_data(self, bvd_id):
        return self._fetch_data(
            DataResult, lambda: demo_path("company_data", bvd_id), bvd_id, DataSet.ALL,
        )

    def fetch_registry_data(self, bvd_id):
        return self._fetch_data(
            RegistryResult,
            lambda: demo_path("registry", bvd_id),
            bvd_id,
            DataSet.REGISTRY,
        )

    def fetch_ownership_data(self, bvd_id):
        return self._fetch_data(
            OwnershipResult,
            lambda: demo_path("ownership", bvd_id),
            bvd_id,
            DataSet.OWNERSHIP,
        )

    def create_record_set(self, name):
        return self._post(
            CreateRecordSetResult,
            lambda: demo_path("create_record_set"),
            f"{self.base_url}/Companies/Store/RecordSets",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            json={"Options": {"Name": name}, "WHERE": [{"BvDID": []}]},
        )

    def add_to_record_set(self, name, bvd_id):
        return self._put(
            AddToRecordSetResult,
            lambda: demo_path("add_to_record_set"),
            f"{self.base_url}/Companies/Store/RecordSets/Add/{name}",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            json={"WHERE": [{"BvDID": [bvd_id]}]},
        )

    def fetch_updates(self, record_set_id, from_datetime, to_datetime):
        return self._get(
            FetchUpdatesResult,
            lambda: demo_path("events"),
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {
                        "WHERE": [
                            {
                                "UpdatedReport": {
                                    "Period": {
                                        "Start": str(from_datetime),
                                        "End": str(to_datetime),
                                    },
                                    "General": ["1", "2", "8",],
                                    "UpdatedCompaniesBasedOnMembershipsWithWocoFlags": [
                                        "COMMON_DIRECTORS_00",
                                        "COMMON_DIRECTORS_01",
                                        "COMMON_DIRECTORS_02",
                                        "COMMON_DIRECTORS_09",
                                    ],
                                    "UpdatedWoco4OwnerShip": [
                                        "Ownership_bo_w",
                                        "Ownership_wof",
                                    ],
                                }
                            },
                            {"AND": [{"RecordSet": str(record_set_id)}]},
                        ],
                        "SELECT": DataSet.UPDATE.fields,
                    }
                )
            },
        )
