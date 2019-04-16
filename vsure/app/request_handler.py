import json
import requests
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from schematics import Model
from schematics.types import ModelType, StringType

from .api.input_types import IndividualData, VSureConfig, VSureCredentials, VisaCheckRequest, VisaHolderData
from .api.errors import VSureServiceException, Error
from .api.output_types import VSureVisaCheckResponse, VisaCheck


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
    visaholder = ModelType(VisaHolderData, required=True)
    key = StringType(required=True)
    visachecktype = StringType(choices=["work", "study"], required=True)


def vsure_request(request_data: VisaCheckRequest):
    return visa_request(request_data.input_data, request_data.config, request_data.credentials)


def visa_request(
        individual_data: 'IndividualData',
        config: 'VSureConfig',
        credentials: 'VSureCredentials',
        is_demo=False):

    model = VSureVisaCheckRequest({
        'visaholder': individual_data.as_visa_holder_data(),
        'key': credentials.api_key,
        'visachecktype': config.visa_check_type})

    url = f'{credentials.base_url}visacheck?type=json&json={json.dumps(model.to_primitive())}'

    session = requests_retry_session()
    try:
        response = session.post(url)
    except Exception as e:
        return {
            "errors": [Error.provider_connection_error(e)]
        }
    finally:
        session.close()

    raw_response, response_model = VSureVisaCheckResponse.from_raw(response)

    if not response_model.output:
        raise VSureServiceException(response_model.error)

    visa_check = VisaCheck.from_raw_data(response_model, config.visa_check_type)

    return {
        'raw': response.json(),
        'output_data': visa_check.to_primitive()
    }
