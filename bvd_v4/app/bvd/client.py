import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry

from app.bvd.datasets import DataSet
from app.bvd.types import SearchResult


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

    def fetch_data(self, bvd_id, dataset=DataSet.ALL):
        field_set = dataset.fields

        response = self.session.get(
            f"{self.base_url}/Companies/data",
            headers={
                "Content-Type": "application/json",
                "ApiToken": self.token,
            },
            params={
                "QUERY": json.dumps({
                    "WHERE": [{"BvDID": bvd_id}],
                    "SELECT": field_set
                })
            }
        )
        json_data = response.json()
        return SearchResult().import_data(json_data)
