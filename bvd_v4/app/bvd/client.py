import json
import logging
import requests

from pycountry import countries
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from schematics.exceptions import (
    DataError,
)

from app.bvd.datasets import DataSet
from app.bvd.types import DataResult, OwnershipResult, SearchResult
from app.passfort.types import Error


def country_alpha_3_to_2(alpha_3):
    try:
        return countries.get(alpha_3=alpha_3).alpha_2
    except (LookupError, AttributeError):
        logging.error(f"Received invalid alpha 3 code from PassFort {alpha_3}")
        return None


def prune_nones(value):
    if isinstance(value, dict):
        return {
            k: prune_nones(v)
            for k, v
            in value.items()
            if v is not None
        }
    if isinstance(value, list):
        return [
            prune_nones(v)
            for v
            in value
        ]
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
    def __init__(self, token):
        self.token = token
        self.session = requests_retry_session()
        self.base_url = "https://Orbis.bvdinfo.com/api/orbis/"
        self.raw_responses = []
        self.errors = []

    def get(self, response_model, *args, **kwargs):
        # TODO: capture http errors
        response = self.session.get(*args, **kwargs)
        self.raw_responses.append(response.json())
        try:
            data = prune_nones(response.json())
            model = response_model().import_data(data, apply_defaults=True)
            model.validate()
            return model
        except DataError as e:
            logging.error({
                "message": "provider response did not match expectation",
                "cause": e.to_primitive(),
                "response": response.json()
            })
            self.errors.append(Error.bad_response(e.to_primitive()))

        return None

    def search(self, name=None, country=None, state=None, company_number=None):
        return self.get(
            SearchResult,
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

    def _fetch_data(self, response_model, bvd_id, data_set=DataSet.ALL):
        return self.get(
            response_model,
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {"WHERE": [{"BvDID": bvd_id}], "SELECT": data_set.fields}
                )
            },
        )

    def fetch_registry_data(self, bvd_id):
        return self._fetch_data(DataResult, bvd_id, DataSet.REGISTRY)

    def fetch_ownership_data(self, bvd_id):
        return self._fetch_data(OwnershipResult, bvd_id, DataSet.OWNERSHIP)
