import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from schematics import Model
from schematics.types import ModelType, StringType

from .api.types import IndividualData, VSureConfig, VSureCredentials, VisaCheckRequest, Error


def requests_retry_session(
        retries=3,
        backoff_factor=0.3,
        session=None,
):
    session = session or requests.Session()
    retry = Retry(
        total=retries,
        read=retries,
        connect=retries,
        backoff_factor=backoff_factor
    )
    adapter = HTTPAdapter(max_retries=retry)
    session.mount('https://', adapter)
    session.timeout = 10
    return session


class VSureVisaCheckRequest(Model):
    visaholder = ModelType(IndividualData, required=True)
    key = StringType(required=True)
    visachecktype = StringType(choices=["work", "study"], required=True)


def vsure_request(request_data: VisaCheckRequest):
    visa_request(request_data.input_data, request_data.config, request_data.credentials)


def visa_request(
        visa_holder: 'IndividualData',
        config: 'VSureConfig',
        credentials: 'VSureCredentials',
        is_demo=False):

    model = VSureVisaCheckRequest({
        'visaholder': visa_holder,
        'key': credentials.api_key,
        'visachecktype': config.visa_check_type})

    url = f'{credentials.base_url}/visacheck?type=json&json={json.dumps(model.to_primitive())}'

    session = requests_retry_session()
    try:
        response = session.post(url)
    except Exception as e:
        return {
            "errors": [Error.provider_connection_error(e)]
        }
    finally:
        session.close()

    return {}
