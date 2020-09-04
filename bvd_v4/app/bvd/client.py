import json
import requests

from pycountry import countries
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app.bvd.datasets import DataSet
from app.bvd.types import DataResult, SearchResult
from app.validation import response_model


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

    @response_model(SearchResult)
    def search(self, name, country, state=None, company_number=None):
        return self.session.get(
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps(
                    {
                        "WHERE": [
                            {
                                "MATCH": {
                                    "Criteria": {
                                        "Name": name,
                                        "Country": countries.get(
                                            alpha_3=country
                                        ).alpha_2,
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

    @response_model(DataResult)
    def fetch_data(self, bvd_id, data_set=DataSet.ALL):
        return self.session.get(
            f"{self.base_url}/Companies/data",
            headers={"Content-Type": "application/json", "ApiToken": self.token},
            params={
                "QUERY": json.dumps({"WHERE": [{"BvDID": bvd_id}], "SELECT": data_set.fields})
            },
        )

