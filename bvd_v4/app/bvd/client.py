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
from app.bvd.types import DataResult, SearchResult
from app.passfort.types import Error


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
            model = response_model().import_data(response.json(), apply_defaults=True)
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
                                            "Country": countries.get(
                                                alpha_3=country
                                            ).alpha_2,
                                            "State": state,
                                        }.items()
                                        if value is not None
                                    }
                                }
                            }
                        ],
                        "SELECT": [
                            "BVDID",
                            "MATCH.NAME",
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

    def fetch_data(self, bvd_id, data_set=DataSet.ALL):
        return self.get(
            DataResult,
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {"WHERE": [{"BvDID": bvd_id}], "SELECT": data_set.fields}
                )
            },
        )
