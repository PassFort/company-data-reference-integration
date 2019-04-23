import json
import requests
from flask import abort
from requests.adapters import HTTPAdapter
from requests.packages.urllib3.util.retry import Retry
from schematics import Model
from schematics.exceptions import DataError
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

    request_model = VSureVisaCheckRequest({
        'visaholder': individual_data.as_visa_holder_data(),
        'key': credentials.api_key,
        'visachecktype': config.visa_check_type.lower()})

    try:
        request_model.validate()
    except DataError as e:
        raise VSureServiceException('{}'.format(e), raw_response)

    url = f'{credentials.base_url}visacheck?type=json&json={json.dumps(request_model.to_primitive())}'

    session = requests_retry_session()

    proxy_url = os.environ.get('VSURE_PROXY_URL')
    proxies = {}
    if proxy_url:
        proxies = {
            'https': proxy_url
        }

    try:
        response = session.post(url, proxies=proxies)
    except Exception as e:
        return {
            "errors": [Error.provider_connection_error(e)]
        }
    finally:
        session.close()

    try:
        response_json = response.json()
    except JSONDecodeError as e:
        raise VSureServiceException('{}'.format(e), response)

    raw_response, response_model = VSureVisaCheckResponse.from_json(response_json)

    if not response_model.output:
        raise VSureServiceException(response_model.error, raw_response)

    try:
        visa_check = VisaCheck.from_visa_check_response(response_model, config.visa_check_type)
    except DataError as e:
        raise VSureServiceException('{}'.format(e), raw_response)

    return {
        'raw': raw_response,
        'output_data': visa_check.to_primitive()
    }
